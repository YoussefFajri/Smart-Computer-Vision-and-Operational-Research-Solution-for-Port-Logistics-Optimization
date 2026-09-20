theme: seriphbackground: https://images.unsplash.com/photo-1494412574643-ff11b0a5c1c3?auto=format&fit=crop&w=1920&q=80title: Solution Intelligente Logistique Portuaire - Marsa Marocinfo: Soutenance PFE Master D3SI - Fajri Youssefclass: text-centerhighlighter: shikilineNumbers: falsedrawings: persist: falsetransition: slide-leftmdc: truestyle: | section { font-family: 'Segoe UI', Helvetica, Arial, sans-serif; color: #1A1A1A; } h1 { color: #0B2B5E; border-bottom: 3px solid #E65100; padding-bottom: 10px; display: inline-block; } h2, h3 { color: #0B2B5E; } strong { color: #0B2B5E; } .marsa-card { background-color: #F8F9FA; border-left: 5px solid #E65100; padding: 15px; border-radius: 4px; margin-top: 10px; } .kpi-box { background: linear-gradient(135deg, #0B2B5E 0%, #15407F 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; } .slidev-vclick-target { transition: opacity 0.5s ease, transform 0.5s ease; } .slidev-vclick-hidden { opacity: 0; transform: translateY(15px); }
Solution Intelligente de Vision par Ordinateur et d'Optimisation Logistique Portuaire
Automatisation de la Gestion des Conteneurs par IA pour Marsa Maroc

Soutenance de Projet de Fin d'Études
Master Data Science & Sécurité des Systèmes d'Information (D3SI)
Présenté par : FAJRI Youssef
Encadrant Académique : Pr. KICH Ismail
Organisme d'accueil : Marsa Maroc
Encadrant Professionnel : M. Mohamed QODSI
Année Universitaire 2025 - 2026
layout: default
Plan de la Présentation
1. Contexte & Problématique
Enjeux du commerce maritime
Marsa Maroc & inefficacités opérationnelles
2. État de l'Art & Mathématiques
Deep Learning (YOLOv8, CIoU, DFL)
OCR (CRAFT, CRNN, CTC)
Recuit Simulé & Fonction d'Énergie
3. Architecture & Conception
Microservices Docker & Apache Kafka
Base de données PostgreSQL & API Flask
Jumeau Numérique 3D (Three.js)
4. Implémentation & Résultats
Algorithme Segment-and-Stitch
Évaluations (96.1% mAP, Re-handling sous 12%)
Conclusion & Perspectives
layout: default
Contexte Logistique Portuaire
Le Défi du Commerce Maritime & des Terminaux à Conteneurs
Volume Mondial Massif : Plus de 80% des échanges mondiaux s'effectuent par voie maritime.
Le Conteneur ISO 6346 : Matricule unique à 11 caractères servant de carte d'identité logistique.
Problématique du Quai : Le pointage manuel sous les portiques STS engendre 4,8% d'erreurs et ralentit les cycles.
Congestion du Parc (Yard) : L'empilement non optimisé provoque un fort taux de re-handling (39,5% observé à Casablanca).
Objectif du PFE : Concevoir une plateforme intelligente combinant Vision par Ordinateur et Recherche Opérationnelle pour automatiser le pointage et optimiser le placement.
layout: image-rightimage: /architecture_diagram.png
Architecture Microservices Globale
Découplage Ingestion & Traitement IA
Ingestion (Edge) : Caméras IoT ➔ Publication asynchrone dans Apache Kafka.
Worker IA Consommateur : Dépilement multi-thread des trames, inférence YOLOv8 + OCR avec gestion du Backpressure.
Logique Métier : API REST Flask communicant avec PostgreSQL.
Supervision (Frontend) : Dashboard Streamlit intégrant le rendu 3D Three.js.
Déploiement : Conteneurisation totale via Docker Compose.
layout: default
Mathématiques : Détection YOLOv8
Activation SiLU
SiLU(x)=x⋅σ(x)=1+e−xx​

Dérivable partout, évite le problème du gradient mourant.

Perte CIoU
LCIoU​=1−IoU+c2ρ2​+αv

Pénalise la distance des centres et le ratio d'aspect.

Perte DFL
LDFL​=−((yi+1​−y)logSi​+(y−yi​)logSi+1​)

Modélise l'incertitude des frontières floues.

Résultat : Inférence à 22 ms/trame sur GPU (RTX 4060) avec 96,1% mAP@0.5.
layout: default
Optimisation Yard : Recuit Simulé
Formalisation de la Fonction de Coût E(s)
Le problème d'allocation (NP-difficile) est résolu par une métaheuristique minimisant l'énergie E(s) :

E(s)=w1​I(Dnew​<Dtop​)+w2​I(Wnew​>Wtop​)+w3​Dmax​Dquai​​+w4​Hmax​Hs​​

Critère de Metropolis
P(acceptation)=exp(−TΔE​) Permet d'accepter des placements sous-optimaux pour échapper aux minima locaux.

Schéma de Refroidissement
Tk+1​=α⋅Tk​(α=0.90) Décroissance géométrique guidant l'attribution (Bay, Stack, Tier) selon la règle EDD.

layout: default
Pipeline OCR : Segment-and-Stitch
Traitement des Matricules Verticaux (ISO 6346)
Binarisation : Extraction des composantes connexes par seuillage d'Otsu.
Tri Vertical (Y) : Ordonnancement des lettres de haut en bas.
Crop & Stitch : Découpage individuel et réassemblage en bande horizontale.
EasyOCR & Early Exit : Lecture avec arrêt immédiat dès validation Regex r"\b[A-Z]{4}\s*\d{6,7}\b".
1,3 seconde
Latence OCR moyenne par conteneur (Réduction de 83%)
layout: two-cols
Détection et Pointage Quai
Pipeline de Vision
Modèle : YOLOv8n (320x320 px)
Classes : Conteneur & Plaque ISO
Précision : 96,1% mAP@0.5
Intégration
Sauvegarde asynchrone dans PostgreSQL.
Vérification instantanée avec le manifeste navire.
Déclenchement du moteur d'optimisation Yard.
::right::

Détection annotée
Matricule validé : CAIU 3212854
Confiance YOLO : 89% | OCR : 95.8%
layout: image-rightimage: /screenshot_yard_3d.png
Jumeau Numérique 3D & Supervision
Interface Streamlit & Three.js
Rendu WebGL 3D : Visualisation géospatiale exacte du parc (Blocs, Baies, Rangées, Tiers).
Optimiseur interactif : L'algorithme propose visuellement l'emplacement idéal pour éviter les doubles manipulations.
Reporting LLM : Génération de synthèses PDF automatisées par un Large Language Model commentant les anomalies de la journée.
Dashboard unifié : Centralisation des KPIs, historique des détections et état du parc.
layout: centerclass: text-center
Résultats Expérimentaux
96,1%
Précision mAP@0.5
(Détection YOLOv8)
85%
Taux de réussite OCR
(Horizontal + Vertical)
≤ 12%
Taux de Re-handling
(À 95% de remplissage)
Gain Global : Réduction de plus de 75% des doubles manipulations comparé au système manuel existant.
layout: default
Conclusion & Perspectives
Bilan des Réalisations
Pipeline de vision par ordinateur opérationnel (YOLOv8 + EasyOCR).
Moteur combinatoire (EDD + Recuit Simulé) validé et fonctionnel.
Architecture temps réel résiliente (Kafka + Flask).
Jumeau numérique 3D et comptes-rendus LLM automatisés.
Perspectives Smart Port
Edge Computing : Déploiement sur cartes NVIDIA Jetson sur portiques STS (30 FPS).
Modèle OCR Personnalisé : Entraînement d'un CRNN dédié aux polices ISO 6346 (> 98%).
Intégration TOS : Synchronisation directe avec le Terminal Operating System de Marsa Maroc.
Application Mobile : Instructions spatiales en temps réel pour les grutiers RTG.
layout: centerclass: text-center
Merci de votre attention
Avez-vous des questions ?
FAJRI Youssef — Master D3SI — USMS / FPBM — Marsa Maroc (2025-2026)