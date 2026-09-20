---
marp: true
theme: default
paginate: true
backgroundColor: #f8fbff
---

# 🚢 Solution Intelligente de Vision par Ordinateur et d’Optimisation Logistique Portuaire

**Automatisation de la Gestion des Conteneurs par IA pour Marsa Maroc**

**Présenté par :** M. Fajri Youssef
**Encadrants :** Pr. Ismail Kich (Académique) & M. Mohamed Qodsi (Professionnel)
**Organisme d'accueil :** Marsa Maroc
**Diplôme :** Master D3SI – 2025/2026

---

## Plan de la présentation

1. **Contexte et Problématique** (Slides 3-7)
2. **État de l'Art et Fondements Mathématiques** (Slides 8-17)
3. **Architecture et Conception** (Slides 18-20)
4. **Implémentation et Algorithmes Clés** (Slides 21-24)
5. **Résultats et Évaluations** (Slides 25-28)
6. **Conclusion et Perspectives** (Slides 29-30)

---

## 1. Présentation de Marsa Maroc

- **Leader** de l'exploitation des terminaux portuaires au Maroc (9 ports stratégiques).
- **Chiffre d'affaires :** ~4 milliards de MAD.
- **Effectif :** Plus de 2 500 collaborateurs.
- **Enjeu majeur :** Optimiser le temps d'escale des navires et maximiser l'efficacité des grues pour rester compétitif à l'international.

---

## 2. Le Flux Logistique Portuaire

Le parcours d'un conteneur suit une chaîne précise :
1. **Quai :** Déchargement par portiques STS (*Ship-to-Shore*).
2. **Transport :** Camions tracteurs portuaires.
3. **Yard (Parc) :** Stockage par grues RTG en blocs, baies, rangées et niveaux.
4. **Livraison :** Sortie du port sur camions externes.

---

## 3. Problématique 1 - Saisie Manuelle des Identifiants

- Lecture visuelle et saisie manuelle des codes ISO 6346 par les opérateurs au quai.
- **Conséquences :**
  - Erreurs humaines (fatigue, mauvaises conditions climatiques).
  - Écarts entre le stock logique et le stock physique.
  - Ralentissement des cycles de déchargement des portiques STS.

---

## 4. Problématique 2 - Le Re-handling (Double Manipulation)

- Mauvaise allocation spatiale des conteneurs dans le parc de stockage (Yard).
- Un conteneur partant bientôt est bloqué sous un conteneur partant plus tard.
- **Conséquences :**
  - Surconsommation de carburant pour les grues RTG.
  - Usure prématurée du matériel.
  - Perte de temps significative pour les camions externes.

---

## 5. Objectifs du Projet

Pour résoudre ces problèmes, nous avons conçu un système intégré reposant sur 3 axes :
1. **Automatisation au Quai :** Caméras IoT + Deep Learning (YOLOv8 + OCR) pour lire les codes automatiquement.
2. **Optimisation du Parc :** Algorithme mathématique pour calculer le meilleur emplacement de stockage.
3. **Aide à la Décision :** Tableau de bord interactif avec jumeau numérique 3D et rapports automatisés.

---

## 6. Intelligence Artificielle et CNN

- Les Réseaux de Neurones Convolutifs (CNN) extraient des caractéristiques visuelles directement des pixels.
- **Fonction Mathématique - La Convolution 2D :**

$$ S(i, j) = (I * K)(i, j) = \sum_{m'} \sum_{n'} I(i-m', j-n') K(m', n') $$

- *Explication :* Le filtre $K$ glisse sur l'image $I$ pour détecter des contours et des textures fondamentales.

---

## 7. Architecture YOLOv8 (You Only Look Once)

- *One-Stage Detector* : Détection ultra-rapide en une seule passe de réseau.
- **3 Composants clés :**
  1. **Backbone (CSPDarknet) :** Extraction des caractéristiques visuelles.
  2. **Neck (PANet) :** Fusion des informations à différentes échelles.
  3. **Head (Découplée et Anchor-Free) :** Prédiction séparée des classes et des boîtes englobantes.

---

## 8. Mathématiques de YOLOv8 - Fonction d'Activation SiLU

- YOLOv8 remplace la fonction ReLU par la fonction **SiLU** (*Sigmoid Linear Unit*) pour une meilleure convergence pendant l'entraînement.
- **Équation :**

$$ \text{SiLU}(x) = x \cdot \sigma(x) = \frac{x}{1 + e^{-x}} $$

- *Explication :* Contrairement à ReLU qui annule brutalement les valeurs négatives, SiLU lisse ces valeurs, ce qui évite le problème du "gradient qui meurt".

---

## 9. Mathématiques de YOLOv8 - Perte CIoU (Complete IoU)

- Comment évaluer la qualité d'une boîte de détection ? Avec la perte **CIoU**.
- **Équation :**

$$ L_{CIoU} = 1 - IoU + \frac{\rho^2(b, b_{gt})}{c^2} + \alpha v $$

- *Explication :* Elle pénalise l'écart de chevauchement ($IoU$), la distance normalisée entre les centres des boîtes ($\rho^2/c^2$), et le ratio d'aspect ($v$).

---

## 10. Mathématiques de YOLOv8 - Perte DFL (Distribution Focal Loss)

- Pour gérer l'incertitude des bords flous, YOLOv8 prédit une distribution de probabilité sur un intervalle discret.
- **Équation :**

$$ L_{DFL}(y_i, y_{i+1}) = - ((y_{i+1} - y) \log(S_i) + (y - y_i) \log(S_{i+1})) $$

- *Explication :* Force le réseau à donner de fortes probabilités ($S_i, S_{i+1}$) aux positions discrètes entourant la vraie coordonnée continue $y$.

---

## 11. Pipeline OCR (Reconnaissance Optique de Caractères)

- **Étape 1 : Détection (CRAFT)**
  - Détecte le texte au niveau du caractère individuel.
  - Génère deux cartes : *Region Score* (centre du caractère) et *Affinity Score* (lien entre caractères).
- **Étape 2 : Reconnaissance (CRNN + CTC)**
  - CNN extrait les caractéristiques, LSTM analyse l'ordre séquentiel des lettres.

---

## 12. Le Décodage CTC (Connectionist Temporal Classification)

- **Algorithme clé :** Permet d'entraîner le réseau sans aligner manuellement chaque lettre à sa position exacte.
- *Mécanisme :* Le réseau prédit des doublons et des vides (ex: M-S-S-C-U-U-ε).
- **Fonctionnement :**
  1. Fusion des caractères identiques consécutifs (S-S devient S).
  2. Suppression des caractères vides (ε).
  - *Résultat final : "MSCU".*

---

## 13. Le Problème d'Allocation de Parc (Yard Stacking)

- Comment positionner les conteneurs pour éviter le shuffling ? C'est un problème d'optimisation combinatoire (NP-difficile).
- **Contrainte 1 - Règle EDD (Earliest Due Date) :**

$$ D(c_{new}) \geq D(c_{top}) $$
*(Le conteneur du dessus doit partir après celui du dessous).*

- **Contrainte 2 - Stabilité Physique :**

$$ W(c_{new}) \leq W(c_{top}) $$
*(Le conteneur du dessus doit être plus léger).*

---

## 14. Algorithme du Recuit Simulé (Simulated Annealing)

- Lorsque le parc est plein, trouver la solution optimale est complexe. Le Recuit Simulé évite de rester bloqué dans un minimum local.
- **Fonction Mathématique - Distribution de Boltzmann (Critère de Metropolis) :**

$$ P(\text{acceptation}) = \exp\left(\frac{-\Delta E}{T}\right) $$

- *Explication :* Si $\Delta E \geq 0$ (solution moins bonne), elle est acceptée avec une probabilité $P$. Au début (Température $T$ élevée), on explore beaucoup. À la fin ($T$ faible), on exploite la meilleure solution.

---

## 15. Schéma de Refroidissement du Recuit Simulé

- L'efficacité de l'algorithme repose sur un refroidissement progressif et contrôlé.
- **Équation de décroissance géométrique :**

$$ T_{k+1} = \alpha \cdot T_k $$

- *(avec $\alpha$ généralement compris entre 0,85 et 0,98).*
- L'algorithme converge ainsi de manière stable vers l'emplacement optimal global minimisant le risque de re-handling.

---

## 16. Architecture Globale du Système

- **Flux asynchrone :** Caméra $\rightarrow$ Kafka $\rightarrow$ Worker IA (YOLO+OCR) $\rightarrow$ API Flask $\rightarrow$ Dashboard Streamlit.
- Découplage total entre la capture vidéo et le traitement IA lourd.

---

## 17. Diagramme de Classes - Module IA & OCR

- **ContainerDetector :** Localise le conteneur, génère la boîte englobante (Bounding Box) et découpe l'image (Crop).
- **OCRReader :** Reçoit le crop, applique les prétraitements et extrait le code ISO 6346.

---

## 18. Conception Base de Données & API REST

- **Modèle Relationnel :** Tables *Containers*, *Manifests*, *Sessions*.
- **API REST (Flask) :**
  - `POST /detect` : Détection synchrone.
  - `GET /stats` : KPIs logistiques.
  - `POST /yard/optimize` : Exécute le Recuit Simulé.
  - `GET /yard/state` : Fournit l'état 3D du parc.

---

## 19. Algorithme "Segment-and-Stitch" (OCR Vertical)

- **Le Défi :** Lire les codes verticaux sur les portes des conteneurs (EasyOCR échoue car il lit de gauche à droite).
- **L'Algorithme innovant :**
  1. Binarisation de l'image et détection des composants connectés.
  2. Tri des caractères de haut en bas (coordonnée Y).
  3. Découpage (Crop) de chaque caractère individuellement.
  4. Redimensionnement et assemblage horizontal (Stitch).
  5. Envoi de l'image reconstruite à l'OCR.

---

## 20. Optimisation de l'OCR - Multi-pipelines & Early Exit

- Application séquentielle de 6 filtres de prétraitement (CLAHE, HSV, Seuillage Otsu, etc.).
- **Algorithme d'Early Exit (Sortie Anticipée) :**
  - Validation par Regex : `r"\b[A-Z]{4}\s*\d{6,7}\b"`
  - Dès qu'un filtre génère un code valide avec une confiance $> 25\%$, le processus s'arrête.
  - *Gain :* Réduction du temps de calcul de 8 secondes à 1,3 seconde.

---

## 21. Implémentation du Worker Asynchrone (Kafka)

- **Défi réseau :** L'OCR est lent, Kafka risque de se déconnecter (Timeout).
- **Solution : Architecture Multi-Thread avec Backpressure (Contre-pression).**
  - **Thread Consommateur :** Lit Kafka en continu, remplit une file d'attente (Queue).
  - **Thread Worker :** Exécute l'IA en continu depuis la Queue.
  - **Algorithme :** Si la Queue est pleine, on "drop" (supprime) la frame la plus ancienne pour éviter l'effondrement mémoire.

---

## 22. Intégration du Jumeau Numérique 3D (Three.js)

- Intégration d'un canvas WebGL dans Streamlit via iframe.
- Récupération de l'état du parc via l'API Flask (`/yard/state`).
- Instanciation dynamique de boîtes 3D (`BoxGeometry`) avec couleurs selon la taille (20/40 pieds) et l'échéance.

---

## 23. Évaluation du Modèle YOLOv8

- **Tableau de performances (Validation) :**
  - Précision : 94,2%
  - Rappel (Recall) : 91,5%
  - mAP@0.5 : 96,1%
- **Temps d'inférence :**
  - CPU : 450 ms (acceptable)
  - GPU (RTX 4060) : 22 ms (idéal pour le temps réel)

---

## 24. Évaluation du Pipeline OCR

- **Taux de réussite par pipeline :**
  - Horizontal (Isolation HSV) : 88,2%
  - Vertical (Segment-and-Stitch) : 78,4%
  - **Combinaison globale avec Early Exit : 85%**
- Le prétraitement adaptatif est indispensable pour contrer la rouille et le manque de lumière.

---

## 25. Évaluation de l'Optimisation du Yard (Recuit Simulé)

- Simulation de 100 conteneurs avec une charge variable.
- **Résultats du taux de Re-handling :**
  - Charge 30-50% : Aléatoire (26%) | EDD simple (4%) | **EDD + Recuit Simulé (0%)**
  - Charge 90-95% : Aléatoire (58%) | EDD simple (38%) | **EDD + Recuit Simulé (12%)**
- *Conclusion :* Réduction de plus de 75% des doubles manipulations, même dans un parc saturé.

---

## 26. Analyse des Interfaces (Dashboard - 1/2)

- **Vue Principale :** Affichage en temps réel des images capturées par les caméras.
- L'IA YOLOv8 y détecte automatiquement les conteneurs et trace les boîtes englobantes.
- Affichage des KPIs (taux d'erreur, temps d'inférence).

---

## 27. Analyse des Interfaces (Dashboard - 2/2)

- **Vue 3D :** Cœur de l'aide à la décision.
- Visualisation interactive du parc de stockage.
- Mise à jour instantanée de la position des conteneurs calculée par l'optimiseur.

---

## 28. Déploiement Conteneurisé (Docker)

- Architecture conteneurisée pour faciliter le déploiement industriel.
- **5 Conteneurs Docker orchestrés :**
  1. Base de données (PostgreSQL)
  2. Messagerie (Kafka & Zookeeper)
  3. Backend (API Flask)
  4. Worker IA (Deep Learning)
  5. Frontend (Dashboard Streamlit)
- Isolation, portabilité et scalabilité garanties.

---

## 29. Synthèse et Difficultés Surmontées

- **Synthèse :** Plateforme complète intégrant Vision par Ordinateur (YOLO+OCR), Streaming (Kafka), Optimisation Mathématique (Recuit Simulé) et Data Visualization (3D).
- **Difficultés surmontées :**
  - Lecture des codes verticaux (Algorithme *Segment-and-Stitch*).
  - Latence du traitement IA (Optimisation *Early Exit*).
  - Gestion de la congestion réseau (Mécanisme de *Backpressure*).

---

## 30. Perspectives et Remerciements

- **Perspectives d'industrialisation :**
  - Déploiement Edge Computing (GPU NVIDIA Jetson sur les portiques STS).
  - Entraînement d'un réseau CRNN sur-mesure (pour dépasser 98% de réussite OCR).
  - Intégration directe au TOS (Terminal Operating System) de Marsa Maroc.
- **Remerciements :** Pr. Ismail Kich, M. Mohamed Qodsi, et les membres du jury.

**"Je vous remercie pour votre attention. Avez-vous des questions ?"**
