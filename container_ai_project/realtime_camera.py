import cv2
import time
import base64
import json
import uuid
from pathlib import Path
import sys

# Ensure backend modules can be imported
sys.path.append(str(Path(__file__).resolve().parent / "backend"))

from model.container_detector import ContainerDetector

# Configuration Kafka
import os
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

KAFKA_BROKER = os.getenv("KAFKA_BROKER_URL", "localhost:9094")
KAFKA_TOPIC  = os.getenv("KAFKA_TOPIC", "camera_detections")

COOLDOWN_SECONDS = 10  # Attente entre chaque capture automatique

def init_kafka_producer():
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(2, 8, 1)  # Fix UnrecognizedBrokerVersion pour Apache Kafka 3.7+
        )
        return producer
    except ImportError:
        print("❌ Erreur: kafka-python-ng n'est pas installé.")
        return None
    except Exception as e:
        print(f"⚠️ Erreur Kafka Producer: {e} (Avez-vous lancé docker-compose up ?)")
        return None

def main():
    print("="*60)
    print("   📷 Caméra IoT Connectée (Producteur Kafka)")
    print("="*60)
    
    producer = init_kafka_producer()
    if not producer:
        print("Exiting...")
        return

    # Pointer vers LE VRAI MODÈLE entraîné !
    model_path = Path(__file__).resolve().parent / "model" / "runs" / "marsa_container_model" / "weights" / "best.pt"
    if not model_path.exists():
        print("⚠️ Attention, le modèle spécialisé n'est pas trouvé, on utilise yolov8n.pt (COCO).")
        model_path = "yolov8n.pt"
    
    print("[*] Chargement de l'IA (Edge YOLOv8)...")
    detector = ContainerDetector(model_path=str(model_path), confidence=0.45)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erreur: Impossible d'ouvrir la caméra.")
        return

    print("\n✅ Caméra active en mode STREAMING KAFKA !")
    print(f"👉 Les détections seront envoyées au topic: {KAFKA_TOPIC}")
    print("👉 Appuyez sur 'q' pour quitter.\n")

    last_capture_time = 0
    focus_start_time  = 0   # Moment où le conteneur a été détecté pour la 1ère fois
    FOCUS_DELAY       = 2.0 # Secondes d'attente pour la mise au point

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        current_time   = time.time()
        annotated_frame = frame.copy()
        
        # Détection légère (juste pour repérer un conteneur)
        results_yolo = detector.model.predict(source=frame, conf=0.45, verbose=False)
        
        has_container = False
        if results_yolo and len(results_yolo) > 0:
            for box in results_yolo[0].boxes:
                has_container = True
                break

        # ── Gestion du délai de mise au point ─────────────────────────────────
        cooldown_ok = (current_time - last_capture_time > COOLDOWN_SECONDS)

        if has_container and cooldown_ok:
            if focus_start_time == 0:
                # Première détection  → démarrage du chrono de mise au point
                focus_start_time = current_time
                print("\n🔍 Conteneur détecté ! Stabilisation en cours (2s)...")

            focus_elapsed = current_time - focus_start_time
            focus_left    = FOCUS_DELAY - focus_elapsed

            if focus_left > 0:
                # ── Compte à rebours visible orange ───────────────────────────
                overlay = annotated_frame.copy()
                cv2.rectangle(overlay, (0, 0), (annotated_frame.shape[1], 60), (0, 100, 200), -1)
                cv2.addWeighted(overlay, 0.55, annotated_frame, 0.45, 0, annotated_frame)
                cv2.putText(annotated_frame,
                            f"MISE AU POINT... {focus_left:.1f}s",
                            (10, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 3)
            else:
                # ── Délai écoulé → Capture ! ───────────────────────────────────
                print("\n📸 Image stabilisée ! Envoi dans le tunnel Kafka...")

                # Flash blanc
                cv2.rectangle(annotated_frame, (0, 0),
                               (annotated_frame.shape[1], annotated_frame.shape[0]),
                               (255, 255, 255), 15)

                # Redimensionnement — garder une résolution haute SANS déformer le ratio
                # pour que les caractères horizontaux restent lisibles par l'OCR
                h_orig, w_orig = frame.shape[:2]
                target_w = 1280
                scale = target_w / w_orig
                target_h = int(h_orig * scale)
                resized_frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

                # Encodage Base64 avec qualité maximale pour préserver les détails du texte
                _, buffer = cv2.imencode('.jpg', resized_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                img_b64   = base64.b64encode(buffer).decode('utf-8')

                event_data = {
                    "session_id":  uuid.uuid4().hex[:10],
                    "timestamp":   current_time,
                    "ship_name":   "AUTO-CAMERA KAFKA",
                    "dock_name":   "Quai IoT",
                    "sts_operator":"Systeme Asynchrone",
                    "image_base64": img_b64
                }

                try:
                    future = producer.send(KAFKA_TOPIC, value=event_data)
                    producer.flush()
                    future.get(timeout=10) # Wait for the result to catch any errors like MessageSizeTooLargeError
                    print("⚡ Événement envoyé avec succès ! (Le Worker s'en occupera).")
                except Exception as e:
                    print(f"⚠️ Échec de l'envoi Kafka: {e}")

                last_capture_time = current_time
                focus_start_time  = 0   # Réinitialiser pour la prochaine détection

        else:
            # Pas de conteneur → réinitialiser le chrono de mise au point
            focus_start_time = 0

        # ── Affichage du statut ────────────────────────────────────────────────
        time_left = max(0, COOLDOWN_SECONDS - (current_time - last_capture_time))
        if time_left > 0:
            cv2.putText(annotated_frame, f"Recharge: {int(time_left)}s", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        elif focus_start_time == 0:
            cv2.putText(annotated_frame, "SCAN EN COURS...", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 0), 2)

        cv2.imshow("Caméra IoT - Pipeline Kafka", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
