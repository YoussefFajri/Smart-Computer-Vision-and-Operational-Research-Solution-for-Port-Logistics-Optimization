---
theme: seriph
background: https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=1920&q=80
title: Solution Intelligente Logistique Portuaire - Marsa Maroc
info: Soutenance PFE Master D3SI - Fajri Youssef
class: text-center
highlighter: shiki
drawings:
  persist: false
transition: slide-left
mdc: true
---

# Solution Intelligente Logistique Portuaire

Automatisation de la Gestion des Conteneurs par IA pour Marsa Maroc

<div class="mt-8 text-sm opacity-85">
  <b>Soutenance de Projet de Fin d'Études</b><br>
  Master Data Science & Sécurité des Systèmes d'Information (D3SI)
</div>

<div class="abs-col bottom-10 left-10 text-left text-xs opacity-75">
  <b>Présenté par :</b> FAJRI Youssef<br>
  <b>Encadrant Académique :</b> Pr. KICH Ismail
</div>

<div class="abs-col bottom-10 right-10 text-right text-xs opacity-75">
  <b>Organisme d'Accueil :</b> Marsa Maroc<br>
  <b>Encadrant Professionnel :</b> M. Mohamed QODSI<br>
  Année 2025 - 2026
</div>

---
layout: default
---

# Plan de la Présentation

<div class="grid grid-cols-2 gap-6 mt-6">

<div>

### 1. Introduction & Contexte
- Contexte du commerce maritime mondial
- Présentation de Marsa Maroc
- Problématique & Objectifs du PFE

### 2. Fondements Mathématiques
- Convolution 2D & Filtres CNN
- YOLOv8 (SiLU, Perte CIoU, Perte DFL)
- OCR (CRAFT, CRNN, Perte CTC)
- Recuit Simulé & Critère de Metropolis

</div>

<div>

### 3. Architecture & Conception
- Microservices découplés Apache Kafka
- Modèle relationnel PostgreSQL
- Passerelle API REST Flask

### 4. Réalisation & Résultats
- Algorithme OCR Segment-and-Stitch
- Jumeau Numérique 3D Three.js
- Évaluations (98.5% mAP, -75% re-handling)
- Conclusion & Perspectives Smart Port

</div>

</div>

---
layout: intro
---

# Contexte Logistique Portuaire

### Le Défi du Commerce Maritime & des Terminaux à Conteneurs

* **Volume Mondial Massif** : Plus de 800 millions d'EVP manipulés par an dans le monde.
* **Le Conteneur ISO 6346** : Matricule unique à 11 caractères (ex: `CAIU 3212854`) servant de carte d'identité logistique.
* **Problématique du Quai** : Le pointage manuel sous les portiques STS engendre des retards et des erreurs d'inattention.
* **Congestion du Parc** : L'empilement non optimisé provoque un fort taux de **re-handling** (mouvements parasites des RTG).

---
layout: default
---

# Marsa Maroc & Initiatives Smart Port

<div class="grid grid-cols-2 gap-8">

<div>

### Leader de l'Exploitation Portuaire
* Opérateur majeur sur **9 ports stratégiques** au Maroc.
* Traitement de plus de **80% du trafic maritime commercial** national.
* Chiffre d'affaires annuel de près de 4 milliards de MAD.

</div>

<div>

### Modules R&D Développés dans ce PFE
1. **OCR Vision STS** : Lecture automatique ISO 6346 sous le quai.
2. **Yard Optimizer** : Placement intelligent 3D (EDD + Recuit Simulé).
3. **Supervision 3D & LLM** : Jumeau Three.js et comptes-rendus automatisés.

</div>

</div>

---
layout: quote
---

# Question Centrale de Recherche

> "Comment concevoir et mettre en œuvre une architecture logicielle intelligente combinant vision par ordinateur et optimisation combinatoire pour automatiser le pointage au quai et minimiser le re-handling au parc ?"

---
layout: default
---

# Convolution 2D (Filtres CNN)

### Équation Continue de Convolution 2D

$$S(i, j) = (I * K)(i, j) = \sum_{m'} \sum_{n'} I(i - m', j - n') \, K(m', n')$$

<div class="grid grid-cols-2 gap-6 mt-6">

<div class="bg-slate-50 p-4 rounded-lg border border-slate-200">

#### Extraction des Bords
Localise les arêtes des conteneurs et les contours des caractères gravés du matricule ISO 6346.

</div>

<div class="bg-slate-50 p-4 rounded-lg border border-slate-200">

#### Invariance par Translation
Conserve une détection exacte du conteneur quelle que soit sa vitesse ou sa position sous le portique STS.

</div>

</div>

---
layout: default
---

# Mathématiques de YOLOv8

<div class="grid grid-cols-3 gap-4 mt-4">

<div class="bg-slate-50 p-4 rounded-lg border border-slate-200">

### Activation SiLU

$$\text{SiLU}(x) = x \cdot \sigma(x)$$

Assure une dérivée fluide et évite le problème du gradient qui meurt.

</div>

<div class="bg-slate-50 p-4 rounded-lg border border-slate-200">

### Perte CIoU

$$\mathcal{L}_{CIoU} = 1 - \text{IoU} + \frac{\rho^2}{c^2} + \alpha v$$

Pénalise la distance entre les centres et le ratio d'aspect des boîtes.

</div>

<div class="bg-slate-50 p-4 rounded-lg border border-slate-200">

### Perte DFL

$$\mathcal{L}_{DFL} = -\Big((y_{i+1}{-}y)\log S_i + (y{-}y_i)\log S_{i+1}\Big)$$

Optimise la régression discrète sur les bordures floues.

</div>

</div>

<div class="mt-6 text-center text-sm font-semibold text-blue-900">
  Inférence ultrarapide à 22 ms/trame sur GPU RTX 4060 avec 98.5% mAP@0.5.
</div>

---
layout: default
---

# Optimisation Yard : Recuit Simulé

<div class="grid grid-cols-2 gap-8">

<div>

### Critère de Metropolis

$$P(\text{acceptation}) = \exp\left(\frac{-\Delta E}{T}\right)$$

Permet au système d'accepter temporairement des placements sous-optimaux pour s'affranchir des minima locaux lorsque le parc est encombré (>75%).

</div>

<div>

### Schéma de Refroidissement

$$T_{k+1} = \alpha \cdot T_k \quad (\alpha \approx 0.95)$$

Décroissance géométrique guidant l'attribution de la coordonnée $(Bay, Stack, Tier)$ selon la règle EDD (*Earliest Due Date*).

</div>

</div>

<div class="mt-8 text-center text-sm font-semibold text-emerald-800">
  Réduction mesurée de 75% du shuffling des grues RTG au parc.
</div>

---
layout: image-right
image: /template_D3SI/images/architecture_diagram_white.png
---

# Architecture Microservices Kafka

### Découplage Ingestion & Traitement IA

* **Producteur Edge STS** : Publication asynchrone des flux vidéo dans le topic `container-video-stream`.
* **Worker Consommateur** : Dépilement multi-thread des trames et inférence GPU sans perte d'images.
* **API REST Flask** : Stockage PostgreSQL et exposition WebSockets pour les clients.

---
layout: image-left
image: /template_D3SI/images/database_schema.png
---

# Modèle Relationnel PostgreSQL

### Tables Principales

* **Containers** : Matricule ISO 6346, armateur, poids, type et Due Date.
* **Passages** : Horodatage quai STS, score de confiance OCR, image cropée.
* **Movements** : Suivi 3D des coordonnées $(Bay, Stack, Tier)$.
* **YardSlots** : Cartographie physique et état d'occupation du parc.

---
layout: default
---

# Algorithme OCR Segment-and-Stitch

### Traitement des Matricules Verticaux

1. **Binarisation** : Extraction des composants connexes par seuillage adaptatif.
2. **Tri Y** : Ordonnancement vertical des lettres de haut en bas.
3. **Crop & Stitch** : Découpage individuel et reconstitution en bande horizontale G-à-D.
4. **EasyOCR & Early Exit** : Lecture avec arrêt immédiat dès validation Regex `r"\b[A-Z]{4}\s*\d{6,7}\b"`.

<div class="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200 text-center font-semibold text-sm">
  Gain de performance : Latence OCR réduite de 8.0s à 1.3s par conteneur (-83%).
</div>

---
layout: two-cols
---

# Détection et Pointage Quai

::left::

### Capture Brute
![Capture d'entrée](/template_D3SI/images/capture_original.jpg)

::right::

### Résultat YOLOv8 + OCR
![Détection annotée](/template_D3SI/images/annotated_container2.jpg)

<div class="col-span-2 text-center text-xs mt-2 font-mono">
  Matricule validé : CAIU 3212854 | Confiance YOLO : 89% | Confiance OCR : 95.8%
</div>

---
layout: two-cols
---

# Jumeau Numérique 3D & Supervision

::left::

### Jumeau 3D (Three.js / WebGL)
![Jumeau 3D](/template_D3SI/images/yard_3d_view.png)

::right::

### Dashboard MARSA AI (Streamlit)
![Dashboard Streamlit](/template_D3SI/images/dashboard_overview.png)

---
layout: fact
---

# 98.5% mAP
Précision de détection YOLOv8 sous les portiques quai STS

---
layout: fact
---

# -75% Re-handling
Réduction du shuffling des grues RTG au parc grâce au Recuit Simulé

---
layout: default
---

# Conclusion & Perspectives

<div class="grid grid-cols-2 gap-8">

<div>

### Bilan des Réalisations
* Pipeline de vision par ordinateur opérationnel au quai.
* Moteur combinatoire (EDD + Recuit Simulé) validé.
* Jumeau numérique 3D et comptes-rendus LLM automatisés.

</div>

<div>

### Perspectives Smart Port
* Déploiement Edge Computing (NVIDIA Jetson sous STS).
* Extension aux 9 terminaux de Marsa Maroc.
* Intégration directe au TOS de Marsa Maroc via API REST.

</div>

</div>

---
layout: center
class: text-center
---

# Merci de votre attention

### Avez-vous des questions ?

<div class="mt-8 text-xs opacity-75">
  FAJRI Youssef — Master D3SI — USMS / FPBM — Marsa Maroc (2025-2026)
</div>
