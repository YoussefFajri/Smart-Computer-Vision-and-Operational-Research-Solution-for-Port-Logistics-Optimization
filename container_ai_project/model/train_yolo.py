"""
Script d'entraînement personnalisé (Fine-Tuning) pour YOLOv8
──────────────────────────────────────────────────────────

Ce script permet d'entraîner le modèle YOLOv8 sur VOS propres images
de conteneurs afin d'améliorer considérablement la précision.

PRÉREQUIS :
Votre dataset doit être au format "YOLO" avec cette structure stricte :

D:/Mersa_pfe/container_ai_project/datasets/custom_data/
├── data.yaml        <-- Le fichier de configuration (chemin vers les dossiers, classes)
├── train/
│   ├── images/      <-- Vos images d'entraînement (.jpg, .png)
│   └── labels/      <-- Fichiers texte (.txt) avec les coordonnées des boîtes
└── val/
    ├── images/      <-- Vos images de validation
    └── labels/      <-- Fichiers texte (.txt) avec les coordonnées

Exemple du fichier `data.yaml` :
    path: D:/Mersa_pfe/container_ai_project/datasets/custom_data
    train: train/images
    val: val/images
    
    nc: 1
    names: ['container']

EXÉCUTION :
Depuis le terminal PowerShell (dans d:\Mersa_pfe) :
    .\mersa_pfe\Scripts\python.exe container_ai_project\model\train_yolo.py
"""
import os
from pathlib import Path
from ultralytics import YOLO

def train_custom_yolo():
    # ── Configurations ──────────────────────────────────────────────
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    
    # Modèle de base pré-entraîné (pour gagner du temps)
    base_model_path = "yolov8n.pt"  
    
    # Chemin vers votre fichier yaml de dataset
    dataset_yaml = PROJECT_ROOT / "datasets" / "data.yaml"
    
    print("=" * 60)
    print("  🚀  Démarrage de l'entraînement YOLOv8 — Marsa Maroc")
    print("=" * 60)
    
    if not dataset_yaml.exists():
        print(f"❌ ERREUR: Le fichier {dataset_yaml} est introuvable !")
        print("Veuillez placer votre dataset dans le dossier 'datasets' contenant le fichier data.yaml.")
        return

    print(f"[*] Chargement du modèle de base : {base_model_path}")
    model = YOLO(base_model_path)
    
    print(f"[*] Début de l'entraînement avec : {dataset_yaml}")
    # ── Paramètres d'entraînement ──────────────────────────────────
    # Vous pouvez ajuster les "epochs" et "imgsz" selon la puissance de votre PC
    results = model.train(
        data=str(dataset_yaml),
        epochs=50,              # Nombre de passages sur toutes les données
        imgsz=320,              # (TRÈS RÉDUIT) Taille pour PC avec peu de RAM
        batch=1,                # (TRÈS RÉDUIT) 1 seule image par itération pour éviter de faire exploser la mémoire
        patience=10,            # Arrêt anticipé si aucune amélioration après 10 epochs
        project=str(PROJECT_ROOT / "model" / "runs"),  # Dossier de sauvegarde
        name="marsa_container_model", # Nom de l'entraînement
        device="cpu",           # Remplacer par 0 si vous avez une carte graphique NVIDIA forte
    )
    
    # ── Sauvegarde finale ───────────────────────────────────────────
    best_model_path = PROJECT_ROOT / "model" / "runs" / "marsa_container_model" / "weights" / "best.pt"
    print("=" * 60)
    print(f"✅ Entraînement terminé avec succès !")
    print(f"🔥 Le NOUVEAU modèle entraîné est sauvegardé à :")
    print(f"   ► {best_model_path}")
    print("=" * 60)
    print("Pour utiliser ce modèle dans le dashboard, copiez-le et changez le chemin :")
    print("YOLO_MODEL_PATH=model/runs/marsa_container_model/weights/best.pt dans le '.env'")

if __name__ == "__main__":
    train_custom_yolo()
