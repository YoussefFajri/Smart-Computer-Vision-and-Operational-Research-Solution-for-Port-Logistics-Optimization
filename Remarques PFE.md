## **Structure et plan**  {#structure-et-plan}

- Le rapport ne comporte ni résumé ni abstract ni mots-clés, alors que ces éléments sont attendus en tête d'un mémoire de Master (avant la table des matières, p. i). Ajouter une page Résumé/Abstract (150--200 mots chacun) avec 5 mots-clés dans les deux langues.

- Le chapitre 4 occupe 13 pages presque intégralement composées de listings de code, tandis que le chapitre 5 ne consacre que 3 pages aux résultats quantitatifs, le reste étant des captures d'écran (4.1--4.6, p. 46--58 vs 5.1--5.3, p. 59--61). *Déplacer les listings intégraux en annexe et ne conserver dans le chapitre 4 que les 15--20 lignes réellement discutées, puis étendre le chapitre 5.*

- Les chapitres ont une phrase d'introduction mais aucune conclusion ni transition de fin de chapitre (fin des 1.6, 2.5, 3.9, 4.6). *Ajouter un paragraphe « Bilan du chapitre » de 5--8 lignes fermant chaque chapitre et annonçant le suivant.*

- Les captures d'écran d'interface (5.4, p. 61--65) sont placées dans le chapitre « Résultats » alors qu'elles relèvent de la démonstration fonctionnelle et non de l'évaluation. *Les rattacher au chapitre 4 ou à une annexe « Manuel d'utilisation », pour que le chapitre 5 ne contienne que des mesures.*

## **Problématique et objectifs :** {#problématique-et-objectifs}

- Les deux inefficacités sont bien identifiées (1.3.1 et 1.3.2, p. 5) mais aucune mesure de l'existant chez Marsa Maroc n'est donnée : ni taux d'erreur de saisie actuel, ni taux de re-handling observé, ni nombre de mouvements/heure. *Insérer en 1.3 un tableau de 3--4 indicateurs relevés pendant le stage avec la source et la période d'observation.*

- Le tableau SWOT (Table 2, p. 7) est incorrectement composé : les faiblesses (« Dépendance à la qualité de la capture », « calibrer les paramètres du recuit ») s'affichent dans la colonne Forces, et les menaces (« Coût de maintenance », « Cyber-sécurité ») dans la colonne Opportunités. *Refaire le tableau en 4 cellules équilibrées et vérifier le rendu à l'impression.*

- L'entrée « Réduction théorique drastique des re-handles » figure comme une Force alors qu'il s'agit d'une hypothèse non encore validée au moment du cadrage (Table 2, p. 7). *La déplacer en objectif attendu (1.4) et ne laisser en Force que ce qui est acquis.*

## **État de l'art / contexte :** {#état-de-lart-contexte}

- Aucune référence n'est appelée dans le corps du texte : les 15 entrées de la bibliographie (p. 69--70) ne sont citées nulle part entre les pages 1 et 68. *Insérer les appels de citation à chaque affirmation empruntée (formules CIoU/DFL 2.2.4, CRAFT 2.3.1, CTC 2.3.3, recuit simulé 2.5.2) --- c'est la correction la plus urgente du rapport.*

- Le chapitre 2 est un exposé pédagogique des briques utilisées, pas un état de l'art : aucun travail antérieur sur la reconnaissance de codes ISO 6346 ni sur le Yard Stacking Problem n'est recensé ni comparé (2.3, p. 15--18 ; 2.5, p. 19--21). *Ajouter une section 2.6 « Travaux connexes » recensant 8--10 publications récentes (2019--2025), avec un tableau comparatif méthodes / jeux de données / performances.*

- 11 des 15 références sont des pages de documentation d'outils (Ultralytics, Flask, Streamlit, Docker, ReportLab...) et une seule source porte sur l'ordonnancement (réf. \[15\], p. 70). *Rééquilibrer vers au moins 60 % de sources scientifiques évaluées par les pairs, avec DOI, et reléguer les URL de documentation en notes de bas de page.*

- L'affirmation « problème d'optimisation combinatoire connu pour être NP-difficile » (2.5, p. 19) n'est appuyée par aucune référence ni preuve de réduction. *Citer un résultat de complexité publié sur le container relocation/stacking problem, ou retirer la qualification.*

## **Méthodologie et conception :** {#méthodologie-et-conception}

- Le jeu de données d'entraînement n'est décrit nulle part : ni nombre d'images, ni provenance, ni protocole d'annotation, ni répartition train/val/test (5.1, p. 59, se limite à « conditions portuaires réelles »). *Ajouter une section « Jeu de données » indiquant l'effectif, la source des images, l'outil d'annotation, la répartition et les augmentations appliquées.*

- La fonction de coût (l'« énergie » E) minimisée par le recuit simulé n'est jamais formalisée, alors que c'est le cœur de la contribution en recherche opérationnelle : 2.5.2 (p. 20) ne donne que le schéma générique de Boltzmann, et les paramètres T₀, α et le nombre d'itérations ne sont pas fournis. *Écrire E(s) explicitement (pondération des violations EDD, des violations de poids, distance au quai) et donner les valeurs des hyperparamètres retenues avec leur méthode de réglage.*

## **Forme :** {#forme}

- Un bug LaTeX majeur affecte le chapitre 4 : les noms de fichiers contenant un underscore basculent en mode mathématique et absorbent la fin du paragraphe, qui s'affiche en italique, sans espaces, et déborde de la marge droite (p. 46, 48, 50, 52, 54, 56 ; ex. p. 52 « yard_ptimizer.pycontientlastructurededonnes... »). *Échapper les underscores dans le texte courant (commande \\ , ou insertion du nom de fichier dans une commande verbatim) et relire chaque page du chapitre 4 après recompilation.*

- Plusieurs listings débordent du cadre et de la page : le code est coupé en pleine ligne p. 49 (ligne 45), p. 53 (ligne 49) et p. 57, et le numéro de page 51 se superpose au code p. 51. *Utiliser listings/minted avec breaklines=true et découper les extraits à 35 lignes maximum par boîte.*

- La ligature « œ » disparaît systématiquement : « curs battants » (p. 4), « manuvre » (p. 5), « mise en uvre » (p. 35), « le cur de l'aide à la décision » (p. 64). *Rechercher/remplacer toutes les occurrences et vérifier l'encodage UTF-8 du fichier source.*

- Résidus de génération visibles : doublons de glossaire (« Ship-to-Shore (Portique de déchargement) (STS) (Ship-to-Shore) » p. 1 ; « Kafka ! (Kafka !) » p. 18), Markdown non converti (« \*\*caractère individuel\*\* » p. 16 ; « \*\*1,3 seconde\*\* » p. 60), en-tête « Nř » au lieu de « N° » (Table 5, p. 60), et message d'erreur PlantUML affiché dans la Figure 13 (p. 41) : « This syntax is deprecated, you must add \<\<#palegreen\>\>... ». *Configurer le glossaire pour n'afficher la forme longue qu'à la première occurrence, purger les \*\*, corriger l'encodage du « ° » et régénérer la Figure 13.*
