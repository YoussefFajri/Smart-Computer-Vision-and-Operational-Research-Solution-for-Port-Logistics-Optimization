# 🎙️ Script de Présentation Orale PFE (Niveau B1)
**Titre :** Solution Intelligente de Vision par Ordinateur et d'Optimisation Logistique Portuaire pour Marsa Maroc  
**Étudiant :** FAJRI Youssef  
**Encadrant Académique :** Pr. KICH Ismail  
**Encadrant Professionnel :** M. Mohamed QODSI (Marsa Maroc)  
**Formation :** Master Data Science et Sécurité des Systèmes d'Information (USMS / FPBM)  
**Durée estimée :** 12 à 14 minutes (Format 10-15 min)

---

## 📌 Slide 1 — Couverture (0:00 - 0:45)
**Ce que vous dites :**
> *"Bonjour Mesdames et Messieurs les membres du jury.*
> *Je m'appelle FAJRI Youssef et je suis ravi de vous présenter aujourd'hui mon projet de fin d'études pour l'obtention du Master Data Science et Sécurité des Systèmes d'Information.*
> *Mon travail s'intitule : **« Solution Intelligente de Vision par Ordinateur et d’Optimisation Logistique Portuaire pour Marsa Maroc »**.*
> *Ce projet a été réalisé sous la direction académique du Professeur KICH Ismail, et sous la supervision professionnelle de Monsieur Mohamed QODSI au sein de Marsa Maroc.*
> *Je vous remercie pour votre présence."*

---

## 📌 Slide 2 — Sommaire (0:45 - 1:15)
**Ce que vous dites :**
> *"Voici le plan de ma présentation aujourd'hui :*
> *1. Tout d'abord, nous verrons le **Contexte et la Problématique** de Marsa Maroc.*
> *2. Ensuite, nous aborderons l'**État de l'Art et les règles mathématiques**.*
> *3. Puis, je vous présenterai l'**Architecture technique** de notre système.*
> *4. Après cela, nous parlerons de l'**Implémentation et des algorithmes** créés.*
> *5. Nous analyserons les **Résultats obtenus**.*
> *6. Enfin, nous terminerons par la **Conclusion et les perspectives** d'avenir."*

---

## 📌 Slide 3 — Contexte : Marsa Maroc & Flux Logistique (1:15 - 2:00)
**Ce que vous dites :**
> *"Commençons par le contexte.*
> *Marsa Maroc est le leader national de la gestion des ports au Maroc. L'entreprise gère 9 ports très importants, comme Casablanca et Tanger Med.*
> *Le voyage d'un conteneur se fait en 4 étapes simples :*
> *1. Le navire arrive au port.*
> *2. Le conteneur est déchargé au quai par une grande grue appelée **STS**.*
> *3. Un camion transporte le conteneur vers la zone de stockage appelée le **Yard**.*
> *4. Enfin, une autre grue appelée **RTG** empile le conteneur dans le parc avant sa livraison.*
> *L'objectif principal est de réduire le temps d'attente des navires dans le port."*

---

## 📌 Slide 4 — Problématiques : Saisie Manuelle & Re-handling (2:00 - 2:50)
**Ce que vous dites :**
> *"Pendant ce processus, nous avons identifié **deux grands problèmes** :*
> * *Premier problème au quai :* La saisie des codes de conteneurs se fait **manuellement** par des agents. À cause de la fatigue ou de la nuit, il y a **4,8% d'erreurs de saisie**, ce qui ralentit le travail.*
> * *Deuxième problème au parc (Yard) :* Les conteneurs sont souvent empilés sans organisation. Si un conteneur placé tout en bas doit sortir, la grue doit d'abord déplacer les conteneurs du dessus. C'est ce qu'on appelle le **Re-handling** (ou double manipulation), et son taux atteint **39,5%**.*
> *Ces deux problèmes entraînent une perte de temps et une surconsommation de carburant."*

---

## 📌 Slide 5 — Analyse Stratégique : SWOT (2:50 - 3:30)
**Ce que vous dites :**
> *"Pour analyser ce projet, nous avons fait une analyse SWOT :*
> * *Les Forces :* Automatisation du pointage, algorithmes d'optimisation rapides et architecture moderne.*
> * *Les Faiblesses :* Besoin d'une bonne carte graphique (GPU) et sensibilité à la mauvaise météo.*
> * *Les Opportunités :* Moderniser les terminaux et réduire l'empreinte carbone des grues.*
> * *Les Menaces :* Le coût du matériel IoT et les conditions difficiles en mer (le sel et l'humidité)."*

---

## 📌 Slide 6 — Objectifs & Solution Proposée (3:30 - 4:15)
**Ce que vous dites :**
> *"Pour résoudre ces problèmes, nous avons développé une plateforme intelligente avec 3 objectifs :*
> *1. **Vision par Ordinateur (IA) :** Détecter et lire automatiquement le code ISO du conteneur au quai sans intervention humaine.*
> *2. **Optimisation du Stockage :** Calculer la meilleure position dans le parc grâce à un algorithme d'optimisation pour réduire le re-handling à moins de 15%.*
> *3. **Supervision 3D :** Offrir un tableau de bord en 3D avec Three.js pour aider les responsables à visualiser le parc en temps réel."*

---

## 📌 Slide 7 — Détection : YOLOv8 & CNN (4:15 - 5:00)
**Ce que vous dites :**
> *"Passons maintenant à la partie technique et à la détection par IA.*
> *Nous utilisons le modèle **YOLOv8**.*
> *Comment ça marche ? Un réseau de neurones convolutif (CNN) applique des filtres sur l'image pour extraire les contours et les formes du conteneur.*
> *YOLOv8 est un modèle « Single-Stage » : cela veut dire qu'il détecte le conteneur et sa plaque en **une seule étape**, ce qui rend le traitement ultra-rapide en temps réel."*

---

## 📌 Slide 8 — Mathématiques : Détection YOLOv8 (5:00 - 5:45)
**Ce que vous dites :**
> *"Pour entraîner YOLOv8, nous utilisons trois formules mathématiques importantes :*
> *1. **La fonction d'activation SiLU :** Elle aide le réseau à apprendre plus vite sans bloquer les calculs.*
> *2. **La perte CIoU :** Elle vérifie que la boîte de détection est bien centrée autour du conteneur.*
> *3. **La perte DFL :** Elle aide le modèle à rester très précis, même quand les bords de l'image sont flous à cause de la pluie ou de l'obscurité."*

---

## 📌 Slide 9 — Reconnaissance : OCR CRAFT & CRNN (5:45 - 6:30)
**Ce que vous dites :**
> *"Une fois la plaque détectée, il faut lire le texte grâce à un pipeline OCR en deux étapes :*
> *1. **CRAFT :** Ce modèle cherche et localise précisément l'emplacement de chaque lettre sur la plaque.*
> *2. **CRNN (CNN + Bi-LSTM) :** Le CNN extrait l'image des lettres, et le réseau Bi-LSTM lit la séquence de gauche à droite pour prédire le mot exact."*

---

## 📌 Slide 10 — Décodage CTC (6:30 - 7:15)
**Ce que vous dites :**
> *"Quand l'IA lit une image, elle découpe le texte en petites tranches. Elle voit souvent des lettres répétées ou des espaces vides (notés epsilon ε).*
> *Nous utilisons le décodage **CTC (Connectionist Temporal Classification)**.*
> *Les règles sont très simples :*
> *1. On fusionne les lettres identiques consécutives.*
> *2. On efface les espaces vides ε.*
> *Par exemple, la séquence `M-S-S-C-U-U-ε` devient automatiquement le code propre **`MSCU`**."*

---

## 📌 Slide 11 — Optimisation : Stacking & Recuit Simulé (7:15 - 8:00)
**Ce que vous dites :**
> *"Après la lecture du code, il faut placer le conteneur dans le parc.*
> *Nous appliquons la règle **EDD (Earliest Due Date)** : le conteneur qui doit partir le premier doit être placé tout au-dessus de la pile.*
> *Pour trouver le meilleur emplacement parmi des milliers de possibilités, nous utilisons l'algorithme du **Recuit Simulé**.*
> *Grâce au critère de Metropolis, cet algorithme accepte parfois une solution moins bonne au début pour éviter de rester bloqué et trouver l'organisation parfaite."*

---

## 📌 Slide 12 — Architecture Microservices (8:00 - 8:45)
**Ce que vous dites :**
> *"Voici l'architecture globale de notre système.*
> *Nous utilisons une architecture **Microservices Asynchrone** :*
> * *Les caméras IoT* envoient les images au serveur de messagerie **Apache Kafka**.*
> * *Un Worker IA* récupère les images dans Kafka et lance les calculs YOLO et OCR en arrière-plan.*
> *Toutes les données sont stockées dans une base **PostgreSQL**, et une **API Flask** permet de faire le lien avec l'interface utilisateur."*

---

## 📌 Slide 13 — Algorithme "Segment-and-Stitch" (8:45 - 9:30)
**Ce que vous dites :**
> *"Sur beaucoup de conteneurs, les codes ISO sont écrits **verticalement** (de haut en bas).*
> *Les logiciels d'OCR classiques échouent car ils lisent horizontalement.*
> *Pour résoudre cela, j'ai développé l'algorithme **Segment-and-Stitch** en 3 étapes :*
> *1. Isoler chaque lettre.*
> *2. Trier les lettres du haut vers le bas.*
> *3. Re-coller les lettres horizontalement sur une seule ligne.*
> *Grâce à cela, l'OCR lit le code vertical sans aucune erreur."*

---

## 📌 Slide 14 — OCR Optimisé : Early Exit & Kafka Worker (9:30 - 10:15)
**Ce que vous dites :**
> *"Pour rendre le système très rapide, nous avons ajouté deux optimisations :*
> *1. **Early Exit (Sortie anticipée) :** Nous appliquons plusieurs filtres sur l'image. Dès que l'OCR trouve un code valide (format Regex ISO) avec plus de 25% de confiance, le traitement s'arrête immédiatement.*
> *2. **Backpressure :** Si les caméras envoient trop d'images, le système met en pause les nouvelles trames pour ne pas faire planter le serveur.*
> *Résultat : le temps de lecture est passé de **8 secondes à seulement 1,3 seconde** par conteneur !"*

---

## 📌 Slide 15 — Jumeau Numérique 3D & Supervision (10:15 - 11:00)
**Ce que vous dites :**
> *"Pour aider les grutiers et les responsables de Marsa Maroc, nous avons créé un **Jumeau Numérique 3D**.*
> *Dans notre application Web Streamlit, nous avons intégré un canvas WebGL avec la bibliothèque **Three.js**.*
> *Les conteneurs apparaissent en 3D avec des couleurs selon leur statut. Le système montre visuellement au grutier exactement où poser le conteneur."*

---

## 📌 Slide 16 — Résultats Expérimentaux (11:00 - 11:45)
**Ce que vous dites :**
> *"Venons-en aux résultats expérimentaux de notre solution :*
> *1. **Précision de détection (YOLOv8) : 96,1%** mAP@0.5.*
> *2. **Taux de réussite OCR : 85%** (sur textes horizontaux et verticaux).*
> *3. **Taux de Re-handling (double manipulation) : réduit à moins de 12%**, même lorsque le parc est rempli à 95%.*
> *En résumé, notre système réduit de plus de **75%** les mouvements inutiles de conteneurs."*

---

## 📌 Slide 17 — Déploiement Conteneurisé avec Docker (11:45 - 12:15)
**Ce que vous dites :**
> *"Pour installer cette solution facilement sur le terrain, l'application est entièrement conteneurisée avec **Docker Compose**.*
> *Nous avons 5 conteneurs séparés (PostgreSQL, Kafka, Zookeeper, l'API Flask et Streamlit).*
> *Cela garantit une grande stabilité, aucune incompatibilité de logiciel et une installation très simple sur les serveurs de Marsa Maroc."*

---

## 📌 Slide 18 — Conclusion & Perspectives (12:15 - 13:00)
**Ce que vous dites :**
> *"En conclusion, les objectifs de ce Projet de Fin d'Études sont atteints :*
> * Le pipeline IA (YOLOv8 + OCR) est opérationnel.*
> * Le moteur d'optimisation (Recuit Simulé) réduit fortement le re-handling.*
> * Le Jumeau Numérique 3D offre une vision claire du parc en temps réel.*
>
> *Comme perspectives futures :*
> * Nous pouvons installer des cartes matérielles **NVIDIA Jetson** directement sur les grues.*
> * Nous pouvons entraîner un modèle OCR CRNN spécifique pour les polices portuaires.*
> * Et enfin, connecter directement notre système avec le logiciel TOS de Marsa Maroc."*

---

## 📌 Slide 19 — Merci de votre attention (13:00 - 13:30)
**Ce que vous dites :**
> *"Je tiens à exprimer mes sincères remerciements à mon encadrant académique Pr. KICH Ismail, à mon encadrant professionnel M. Mohamed QODSI, ainsi qu'à tous les membres du jury pour votre écoute et vos conseils.*
>
> *Je suis maintenant à votre disposition pour répondre à toutes vos questions.*
> *Merci !"*

---

### 💡 Conseils pour l'oral :
- **Phrases simples** : Ce script utilise un langage de niveau B1, parfait pour s'exprimer avec fluidité sans hésitation.
- **Gestion du temps** : Chaque diapositive prend environ 35 à 45 secondes, ce qui donne une durée totale de 12 à 13 minutes.
- **Accentuations** : Insistez bien oralement sur les chiffres clés (**96,1%**, **85%**, **12%**, **1,3s**).
