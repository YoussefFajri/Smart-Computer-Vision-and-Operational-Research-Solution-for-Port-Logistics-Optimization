"""
Script pour REPRENDRE l'entraînement YOLOv8 mis en pause
────────────────────────────────────────────────────────
Utilisez ce script uniquement si vous avez arrêté "train_yolo.py" 
en cours de route (Ctrl+C) et que vous voulez reprendre là où
l'IA s'était arrêtée sans rien perdre.

EXÉCUTION :
Depuis le terminal PowerShell (dans d:\Mersa_pfe) :
    .\mersa_pfe\Scripts\python.exe container_ai_project\model\resume_yolo.py
"""
import os
from pathlib import Path
from ultralytics import YOLO

def resume_custom_yolo():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    
    # On pointe vers le DERNIER fichier sauvegardé (last.pt) avant l'arrêt
    last_model_path = PROJECT_ROOT / "model" / "runs" / "marsa_container_model" / "weights" / "last.pt"
    
    print("=" * 60)
    print("  🔄  Reprise de l'entraînement YOLOv8 — Marsa Maroc")
    print("=" * 60)
    
    if not last_model_path.exists():
        print(f"❌ ERREUR: Le fichier {last_model_path} est introuvable !")
        print("Avez-vous bien lancé l'entraînement au moins une fois ?")
        return

    print(f"[*] Chargement du dernier point de sauvegarde : {last_model_path}")
    
    # On charge le dernier checkpoint
    model = YOLO(str(last_model_path))
    
    print("[*] Reprise de l'entraînement là où il s'est arrêté...")
    # "resume=True" dit à l'IA de retrouver toutes ses configurations d'origine 
    # et de reprendre exactement à la bonne Epoch.
    results = model.train(resume=True)
    
    print("=" * 60)
    print(f"✅ Entraînement terminé avec succès !")
    print("=" * 60)

if __name__ == "__main__":
    resume_custom_yolo()
