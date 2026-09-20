"""
Kafka Worker — Consommateur Asynchrone Multi-Threadé
────────────────────────────────────────────────────
Ce script tourne en arrière-plan. Il écoute le tunnel Kafka (topic: camera_detections).
Il utilise une architecture multi-threadée non-bloquante avec file d'attente (Queue)
pour éviter les timeouts du consommateur Kafka lors de traitements lourds (YOLOv8 + OCR).
"""
from __future__ import annotations

import os
import sys
import json
import time
import base64
import uuid
import queue
import threading
import traceback
import signal
from pathlib import Path

import cv2
import numpy as np

# Configuration des chemins
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import YOLO_MODEL_PATH, YOLO_CONFIDENCE, STATIC_FOLDER
from backend.services.db_manager import save_container, init_db, get_manifest_container
from model.container_detector import ContainerDetector
from backend.services.ocr_reader import OCRReader, process_image

# Chargement config Kafka
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

KAFKA_BROKER      = os.getenv("KAFKA_BROKER_URL", "localhost:9094")  # Port EXTERNAL Docker
KAFKA_TOPIC       = os.getenv("KAFKA_TOPIC", "camera_detections")
KAFKA_RESULT_TOPIC = os.getenv("KAFKA_RESULT_TOPIC", "container_ids")  # Topic pour résultats OCR

# ── Module-level helper functions for tests and backward compatibility ───────────

def decode_image_base64(base64_str: str) -> np.ndarray:
    img_data = base64.b64decode(base64_str)
    np_arr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

def publish_ocr_result(producer, session_id: str, ocr_results: list, processing_time: float):
    """Publication des résultats OCR (Helper au niveau du module)."""
    if producer is None:
        return

    try:
        result_event = {
            "session_id":      session_id,
            "timestamp":       time.time(),
            "processing_time": processing_time,
            "results": [
                {
                    "container_id":   r.get("container_id"),
                    "raw_text":       r.get("raw_text", ""),
                    "ocr_confidence": r.get("ocr_confidence", 0.0),
                    "is_valid":       r.get("is_valid", False),
                    "pipeline":       r.get("pipeline", "N/A"),
                }
                for r in ocr_results
            ]
        }
        producer.send(KAFKA_RESULT_TOPIC, value=result_event)
        producer.flush()
        print(f"📤 [Kafka] Résultats OCR publiés dans '{KAFKA_RESULT_TOPIC}' ({len(ocr_results)} résultat(s))")
    except Exception as e:
        print(f"⚠️ Échec de publication des résultats: {e}")

# ── Consumer Thread ─────────────────────────────────────────────────────────────

class ConsumerThread(threading.Thread):
    """
    Consomme en continu les messages du topic Kafka et les injecte dans la Queue.
    Fonctionne de manière non-bloquante et super rapide pour éviter les timeouts Kafka.
    """
    def __init__(self, broker: str, topic: str, frame_queue: queue.Queue, shutdown_event: threading.Event):
        super().__init__(name="ConsumerThread")
        self.broker = broker
        self.topic = topic
        self.queue = frame_queue
        self.shutdown_event = shutdown_event
        self.daemon = True

    def run(self):
        print(f"[ConsumerThread] Démarrage du consommateur Kafka sur {self.broker} topic={self.topic}")
        try:
            from kafka import KafkaConsumer
        except ImportError:
            print("[ConsumerThread] ❌ Erreur: kafka-python n'est pas installé.")
            return

        consumer = None
        while not self.shutdown_event.is_set():
            try:
                if consumer is None:
                    consumer = KafkaConsumer(
                        self.topic,
                        bootstrap_servers=[self.broker],
                        auto_offset_reset='latest',
                        enable_auto_commit=True,
                        group_id='marsa-ai-group-v3',
                        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                        api_version=(2, 8, 1),
                        # Configuration robuste pour éviter les timeouts
                        session_timeout_ms=30000,       # Détection déconnexion (30s)
                        heartbeat_interval_ms=10000,    # Heartbeat régulier (10s)
                        max_poll_interval_ms=300000,    # Max 5 min (on polle en permanence donc jamais atteint)
                        request_timeout_ms=40000,
                    )
                    print("[ConsumerThread] ✅ Connecté au Consumer Kafka !")

                # Polling avec un court timeout pour vérifier régulièrement l'état de l'arrêt
                records = consumer.poll(timeout_ms=1000)
                for tp, messages in records.items():
                    for message in messages:
                        if self.shutdown_event.is_set():
                            break

                        data = message.value
                        session_id = data.get("session_id", uuid.uuid4().hex[:10])

                        # Gestion de la contre-pression (Backpressure) : Drop de la frame la plus ancienne si plein
                        if self.queue.full():
                            try:
                                dropped = self.queue.get_nowait()
                                print(f"⚠️ [ConsumerThread] Queue pleine ! Suppression du message le plus ancien. (Session abandonnée : {dropped.get('session_id')})")
                            except queue.Empty:
                                pass

                        self.queue.put(data)
                        print(f"📥 [ConsumerThread] Frame empilée. (Session: {session_id}, Queue: {self.queue.qsize()}/100)")

            except ValueError as e:
                if "Invalid file descriptor" in str(e):
                    print("[ConsumerThread] ⚠️ Connexion Kafka perdue (file descriptor). Reconnexion dans 3s...")
                else:
                    print(f"[ConsumerThread] ❌ Erreur Consumer : {e}")
                
                if consumer:
                    try:
                        consumer.close()
                    except Exception:
                        pass
                    consumer = None
                time.sleep(3)
            except Exception as e:
                print(f"[ConsumerThread] ⚠️ Exception inattendue : {e}")
                traceback.print_exc()
                time.sleep(3)

        if consumer:
            try:
                consumer.close()
                print("[ConsumerThread] Consumer Kafka fermé proprement.")
            except Exception as e:
                print(f"[ConsumerThread] Erreur lors de la fermeture du consumer : {e}")

# ── Worker Thread ───────────────────────────────────────────────────────────────

class WorkerThread(threading.Thread):
    """
    Récupère les frames de la Queue, exécute les modèles lourds (YOLOv8 + OCR)
    dans son propre thread, sauvegarde en BD et publie les résultats.
    """
    def __init__(self, broker: str, result_topic: str, frame_queue: queue.Queue, shutdown_event: threading.Event):
        super().__init__(name="WorkerThread")
        self.broker = broker
        self.result_topic = result_topic
        self.queue = frame_queue
        self.shutdown_event = shutdown_event
        self.daemon = True
        self.producer = None
        self.detector = None
        self.ocr_reader = None

    def init_producer(self):
        try:
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=[self.broker],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(2, 8, 1),
            )
            print("[WorkerThread] ✅ Kafka Producer initialisé.")
        except Exception as e:
            print(f"[WorkerThread] ⚠️ Kafka Producer indisponible : {e} (les résultats ne seront pas publiés)")
            self.producer = None

    def run(self):
        print("[WorkerThread] Démarrage du thread de traitement IA.")

        # Chargement des modèles lourds dans le thread pour ne pas bloquer le démarrage principal
        try:
            print("[WorkerThread] Initialisation de la Base de Données...")
            init_db()

            print("[WorkerThread] Chargement de YOLOv8...")
            self.detector = ContainerDetector(
                model_path=str(PROJECT_ROOT / YOLO_MODEL_PATH),
                confidence=YOLO_CONFIDENCE
            )

            print("[WorkerThread] Chargement de OCRReader...")
            self.ocr_reader = OCRReader()
            
            # Déclenche le chargement d'EasyOCR en mémoire (dynamic GPU)
            self.ocr_reader._get_reader()

            self.init_producer()
            print("[WorkerThread] ✅ Pipeline IA prêt à l'écoute de la Queue.")
        except Exception as e:
            print(f"[WorkerThread] ❌ Erreur fatale d'initialisation des modèles : {e}")
            traceback.print_exc()
            return

        while not self.shutdown_event.is_set():
            try:
                # Lecture de la Queue avec timeout de 1s pour vérifier shutdown_event régulièrement
                try:
                    data = self.queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                session_id = data.get("session_id", uuid.uuid4().hex[:10])
                print(f"\n⚙️ [WorkerThread] Traitement en cours (Session: {session_id}, Queue restante: {self.queue.qsize()})")
                
                t0 = time.perf_counter()

                try:
                    img_b64 = data.get("image_base64")
                    if not img_b64:
                        print(f"[WorkerThread] ❌ Session {session_id} ignorée: aucun attribut image_base64.")
                        self.queue.task_done()
                        continue

                    image = decode_image_base64(img_b64)
                    if image is None:
                        print(f"[WorkerThread] ❌ Session {session_id}: décodage de l'image impossible.")
                        self.queue.task_done()
                        continue

                    # Sauvegarde de l'image originale dans le dossier static
                    img_filename = f"capture_{session_id}.jpg"
                    img_path = STATIC_FOLDER / img_filename
                    STATIC_FOLDER.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(img_path), image)

                    # Inférence YOLOv8
                    det_result = self.detector.detect(
                        image_source=image,
                        save_dir=STATIC_FOLDER,
                        session_id=session_id
                    )

                    print(f"[WorkerThread] YOLO a détecté {len(det_result['detections'])} objet(s)")
                    for i, det in enumerate(det_result["detections"]):
                        print(f"  └─ Box {i}: bbox={det['bbox']}, "
                              f"conf={det.get('confidence', 0):.2f}, "
                              f"class={det.get('class')}")

                    # Inférence OCR
                    ocr_results = self.ocr_reader.read_from_detections(image, det_result["detections"])

                    # Fallback sur image entière si YOLO n'a rien détecté
                    if not ocr_results:
                        print("[WorkerThread] ⚠️ Aucune détection YOLO — OCR sur l'image entière.")
                        _, buffer = cv2.imencode('.jpg', image)
                        full_ocr = process_image(buffer.tobytes())
                        full_ocr["bbox"]            = [0, 0, image.shape[1], image.shape[0]]
                        full_ocr["yolo_confidence"] = 0.0
                        full_ocr["class"]           = "full_image_fallback"
                        ocr_results = [full_ocr]

                    # Logs des résultats OCR
                    for i, ocr in enumerate(ocr_results):
                        print(f"  [OCR Result {i}] ID={ocr.get('container_id')}, "
                              f"raw='{ocr.get('raw_text', '')[:60]}', "
                              f"conf={ocr.get('ocr_confidence', 0):.2f}, "
                              f"pipeline={ocr.get('pipeline', 'N/A')}")

                    # Publication des résultats dans Kafka
                    total_time = round(time.perf_counter() - t0, 3)
                    publish_ocr_result(self.producer, session_id, ocr_results, total_time)

                    # Sauvegarde en Base de données
                    saved_count = 0
                    for ocr in ocr_results:
                        cid = ocr.get("container_id")
                        is_valid_id = bool(cid and cid != "INCONNU")

                        db_data = {
                            "container_id":     cid if is_valid_id else "ILLISIBLE",
                            "confidence_score": ocr.get("yolo_confidence", 0.0),
                            "ship_name":        data.get("ship_name", "Caméra IoT"),
                            "dock_name":        data.get("dock_name", "Inconnu"),
                            "sts_operator":     data.get("sts_operator", "Automatique"),
                            "status":           "détecté" if not is_valid_id else "déchargé",
                            "image_path":       str(img_path),
                            "annotated_path":   det_result["annotated_path"],
                            "ocr_text":         ocr.get("raw_text", ""),
                            "ocr_confidence":   ocr.get("ocr_confidence", 0.0),
                            "processing_time":  det_result["processing_time"],
                        }

                        if is_valid_id:
                            manifest_info = get_manifest_container(cid)
                            if manifest_info:
                                db_data["status"] = "déchargé"
                                db_data["yard_block"] = manifest_info.get("yard_block")
                                db_data["yard_localization"] = manifest_info.get("yard_localization")
                                db_data["yard_tier"] = manifest_info.get("yard_tier")
                                db_data["notes"] = "ID vérifié avec le manifeste."
                            else:
                                db_data["status"] = "non existant"
                                db_data["notes"] = "ID non trouvé dans le manifeste."
                        else:
                            db_data["notes"] = "Texte illisible ou format invalide."

                        save_container(db_data)
                        saved_count += 1

                    print(f"✅ [WorkerThread] Traitement terminé en {total_time}s — {saved_count} conteneur(s) BD.")

                except Exception as e:
                    print(f"❌ [WorkerThread] Erreur lors du traitement asynchrone de la session {session_id} : {e}")
                    traceback.print_exc()
                finally:
                    self.queue.task_done()
                    # Libération de la mémoire
                    import gc
                    gc.collect()

            except Exception as e:
                print(f"[WorkerThread] Erreur de boucle principale : {e}")
                traceback.print_exc()
                time.sleep(1)

        if self.producer:
            try:
                self.producer.close()
                print("[WorkerThread] Producer Kafka fermé proprement.")
            except Exception as e:
                print(f"[WorkerThread] Erreur lors de la fermeture du producer : {e}")

# ── Main function ───────────────────────────────────────────────────────────────

def main():
    print("="*70)
    print("   👷 Démarrage du Worker Kafka Non-Bloquant Multi-Threadé")
    print("="*70)
    print(f"[*] Connexion au broker Kafka: {KAFKA_BROKER} / Topic: {KAFKA_TOPIC}")
    print(f"[*] Topic résultats OCR: {KAFKA_RESULT_TOPIC}")

    # Vérification et logging de la disponibilité du GPU
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        print(f"[*] PyTorch CUDA disponible : {gpu_available}")
        if gpu_available:
            print(f"[*] Périphérique GPU détecté : {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("[*] PyTorch non installé localement.")

    # File d'attente partagée (limite à 100 images max pour éviter la surconsommation de RAM)
    frame_queue = queue.Queue(maxsize=100)
    
    # Event de synchronisation pour l'arrêt propre des threads
    shutdown_event = threading.Event()

    # Création des threads
    consumer_thread = ConsumerThread(
        broker=KAFKA_BROKER,
        topic=KAFKA_TOPIC,
        frame_queue=frame_queue,
        shutdown_event=shutdown_event
    )

    worker_thread = WorkerThread(
        broker=KAFKA_BROKER,
        result_topic=KAFKA_RESULT_TOPIC,
        frame_queue=frame_queue,
        shutdown_event=shutdown_event
    )

    # Capturer les signaux système (SIGINT et SIGTERM) pour un arrêt gracieux
    def handle_shutdown(signum, frame):
        print(f"\n👋 Signal d'arrêt reçu ({signum}). Fermeture des threads en cours...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Démarrage des threads
    worker_thread.start()
    consumer_thread.start()

    print("[*] Threads démarrés. En écoute d'événements (Ctrl+C pour quitter)...")

    # Boucle d'attente active sur le thread principal pour intercepter les signaux
    try:
        while not shutdown_event.is_set():
            consumer_thread.join(timeout=1.0)
            worker_thread.join(timeout=1.0)
            
            # Si un des threads meurt anormalement, on stoppe tout
            if not consumer_thread.is_alive() or not worker_thread.is_alive():
                print("⚠️ Un des threads s'est arrêté de manière inattendue.")
                shutdown_event.set()
                break
    except KeyboardInterrupt:
        print("\n👋 Arrêt demandé via le clavier.")
        shutdown_event.set()

    # Jointure finale des threads
    consumer_thread.join(timeout=5)
    worker_thread.join(timeout=5)
    print("👷 Worker Kafka Multi-Threadé arrêté proprement.")

if __name__ == "__main__":
    main()
