# Documentation Complète du Projet : Port Logistics AI (Marsa Maroc)

Ce document décrit l'architecture complète du projet d'Intelligence Artificielle de détection de conteneurs. Il est conçu pour vous aider à comprendre chaque fichier et son code, notamment dans le cadre de votre Projet de Fin d'Études (PFE).

---

## 🏗️ Architecture Globale

Le projet suit une architecture de type **Microservices**, séparant l'interface visuelle (Frontend), la logique métier (Backend API) et l'Intelligence Artificielle (Deep Learning).

```text
container_ai_project/
│
├── backend/            # Serveur API (Flask)
├── dashboard/          # Interface Utilisateur (Streamlit)
├── model/              # Cerveau de l'IA (YOLOv8)
├── llm/                # Génération de texte automatisée
├── datasets/           # Données d'entraînement pour l'IA
├── docker/             # Fichiers de déploiement en production
└── _test_all.py        # Script de validation globale
```

---

## 📂 1. Le Module d'Intelligence Artificielle (`model/`)

### `model/container_detector.py`
C'est le module de Vision par Ordinateur.
- **Ce que fait le code :** Il utilise la bibliothèque `ultralytics` pour charger le modèle YOLOv8.
- **La méthode `detect()` :** Elle reçoit une image, la lit avec OpenCV (`cv2`), et la passe dans le réseau de neurones (`self.model.predict`). Si le score de confiance (confidence) dépasse le seuil défini (environ 40%), il trace un rectangle vert (Bounding Box) autour du conteneur et sauvegarde cette "image annotée" dans le dossier `static/`.
- **Méthode `crop_region()` :** C'est une fonction mathématique cruciale qui "découpe" uniquement l'endroit où le conteneur a été détecté pour pouvoir l'envoyer à l'étape suivante (la lecture du texte).

### `model/train_yolo.py`
- **Ce que fait le code :** C'est le script d'entraînement personnalisé (Fine-tuning).
- Il prend le petit modèle de base `yolov8n.pt`, lit votre fichier `datasets/data.yaml` pour localiser vos images, et lance une boucle d'apprentissage (`model.train()`). Il a été ajusté avec `imgsz=320` et `batch=1` pour ne pas saturer la mémoire RAM de votre ordinateur pendant la phase très intensive d'apprentissage.

---

## 📂 2. Le Backend et API (`backend/`)

### `backend/app.py`
C'est le point d'entrée de votre serveur web (Flask).
- **Le code :** Il charge la configuration, initialise la base de données (`init_db()`), puis déclare toutes les "routes" (les URLs) comme `/detect`, `/stats`, etc. 
- Il gère également le "Cross-Origin Resource Sharing" (CORS) pour accepter les requêtes venant de n'importe quel ordinateur en réseau.

### `backend/config.py` et `.env`
- Le fichier `.env` sauvegarde secrètement toutes les variables d'environnement (Mots de passe de base de données, chemins absolus, environnement de développement). 
- `config.py` traduit ces variables de texte en objets compréhensibles pour le code Python.

### `backend/services/ocr_reader.py` (La Lecture Optique)
C'est ici qu'on extrait le texte des images.
- **Ce que fait le code :** Il utilise `EasyOCR`. Lorsqu'il reçoit le morceau d'image découpé du conteneur, il scanne le texte.
- **L'expression régulière (Regex) :** Le code contient `re.compile(r'^[A-Z]{4}\d{7}$')`. Cette ligne est vitale : elle dit à l'algorithme "ignore tout le texte détecté, et ne garde que ce qui ressemble au format ISO d'un conteneur (exactement 4 Majuscules suivies de 7 chiffres)".

### `backend/services/db_manager.py` (Base de données)
C'est le pont entre le code Python et la base de données (SQLite/PostgreSQL).
- **Ce que fait le code :** Il utilise "SQLAlchemy" (un ORM). Au lieu d'écrire du code SQL compliqué (comme `INSERT INTO`), ce fichier transforme les opérations en fonctions Python (`save_container()`, `get_stats()`).
- C'est ce fichier qui calcule automatiquement les KPI (Total détecté, taux de réussite OCR, temps de traitement).

### `backend/services/report_gen.py` (Rapport PDF)
- Génère dynamiquement un compte-rendu logistique avec la librairie `reportlab`. 
- Il dessine un tableau contenant les métriques et ajoute un résumé de situation généré sur-mesure.

---

## 📂 3. Génération Autonome (`llm/`)

### `llm/llm_report.py`
C'est le cerveau linguistique qui rédige les rapports de fin de journée.
- **Le code :** Il analyse les statistiques chiffrées de la base de données (ex: *5 conteneurs détectés au Quai 1*). Il utilise soit un dictionnaire (Template) soit une API ("Ollama/Groq" pour faire appel à un véritable modèle de langage style ChatGPT) afin de transformer les mathématiques en un paragraphe de résumé texte destiné au directeur du port.

---

## 📂 4. L'Interface Utilisateur (`dashboard/`)

### `dashboard/dashboard.py`
C'est la partie visuelle conçue avec Streamlit.
- **Structure :** Le code est divisé en blocs "Pages" (`if page == "Vue Générale":`). 
- **Ce que fait le code :**
  - **Les Graphiques :** Il appelle l'API (`requests.get('http://localhost:5000/stats')`). Il prend les résultats JSON et utilise `plotly.express` pour dessiner des graphiques dynamiques (camemberts, histogrammes des activités des 7 derniers jours).
  - **Uploader :** Sur l'onglet Image, un bloc `st.file_uploader()` intercepte votre photo. Il la compresse et l'envoie en HTTP POST vers la route `/detect` de Flask. Il affiche ensuite le retour (la photo annotée en vert et la table OCR).

---

## 📂 5. Déploiement Informatique (`docker/`)

Cette partie correspond à la "Mise en Production".
- **`Dockerfile.backend` et `Dockerfile.dashboard` :** Ce sont les plans de construction ("Recettes de cuisine"). Ils disent à Docker : "Télécharge Linux, installe Python 3.11, copie tous mes fichiers dedans, fais un pip install requirements, et lance le port".
- **`docker-compose.yml` :** C'est le chef d'orchestre. Il allume la Base de donnée, attend qu'elle soit active, puis allume le Backend, et enfin le Dashboard, en liant le tout de manière isolée et sécurisée.

---

## Conclusion pour votre Projet
Ce code prouve la réussite de l'intégration de multiples branches de l'ingénierie moderne :
1. **L'IA de Détection :** YOLOv8 (Deep Learning Visuel).
2. **LLM & OCR :** Extraction de texte et résumé dynamique.
3. **Le Backend :** Création d'une API REST robuste sous Flask et Base de Données SQL.
4. **Data Visualization :** Affichage décisionnel avec Streamlit et Plotly.
5. **DevOps :** Dockerisation de l'environnement complet.
