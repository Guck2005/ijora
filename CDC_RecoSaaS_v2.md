**RecoSaaS**

Plateforme SaaS de Recommandation Intelligente

*Filtrage Collaboratif Item-Item --- Conception from scratch*

  ----------------- -----------------------------------------------------
  **Cadre**         TP1 --- Big Data / Machine Learning

  **Version**       2.0 --- Enrichi & Affiné

  **Date            05 Mai 2026
  livraison**       

  **Document**      Cahier des Charges Fonctionnel

  **Statut**        ✅ Validé pour développement
  ----------------- -----------------------------------------------------

# 1. Présentation du Projet

## 1.1. Contexte

Dans le cadre du TP1 Big Data / Machine Learning, ce projet vise à
dépasser le cadre d'un simple script statique. L'ambition est de
concevoir une véritable plateforme SaaS (Software as a Service)
générique, interactive et prête pour un usage en production, démontrant
une maîtrise complète du cycle de vie d'un produit data.

## 1.2. Objectif Principal

Fournir une application web no-code permettant à tout utilisateur
(entreprise, chercheur, étudiant) de charger son propre jeu de données
transactionnelles et de générer automatiquement des recommandations
personnalisées, sans compétences en programmation.

## 1.3. Proposition de Valeur (Value Proposition)

+-----------------------------------------------------------------------+
| **🎯 Pourquoi RecoSaaS ?**                                            |
|                                                                       |
| ✦ Aucune configuration serveur --- 100 % hébergé sur Streamlit Cloud  |
|                                                                       |
| ✦ Algorithme transparent et explicable (from scratch, pas de boîte    |
| noire)                                                                |
|                                                                       |
| ✦ Compatible avec tout dataset tabulaire : e-commerce, streaming, RH, |
| santé\...                                                             |
|                                                                       |
| ✦ Résultats exportables en CSV, JSON et rapport PDF en un clic        |
|                                                                       |
| ✦ Interface pensée pour les non-techniciens (UX no-code)              |
+-----------------------------------------------------------------------+

# 2. Périmètre Technique et Contraintes

  --------------------- --------------------------- ----------------------
  **Contrainte**        **Détail**                  **Justification**

  Algorithme            Item-Item Collaborative     Imposé par le cahier
                        Filtering                   TP1

  Implémentation        From scratch (NumPy/Pandas  Interdit d'utiliser
                        uniquement)                 Surprise, sklearn
                                                    CF\...

  Similarité            Pearson (au choix           Couverture pédagogique
                        utilisateur)                élargie

  Frontend              Streamlit (Python)          Déploiement simplifié,
                                                    natif Python

  Format entrée         CSV tabulaire               Format universel,
                                                    accessible à tous

  Hébergement           Streamlit Community Cloud   URL publique gratuite

  Python                3.10+, PEP8, commenté       Norme professionnelle

  Police UI             Satori (Google Fonts)       Spécification
                                                    esthétique client
  --------------------- --------------------------- ----------------------

# 3. Parcours Utilisateur (User Journey)

Le flux est conçu en 5 étapes linéaires et guidées pour maximiser
l'accessibilité :

  ------------- ----------------- ------------------------- -------------------
  **Étape**     **Action          **Retour Système**        **Statut CdC
                Utilisateur**                               original**

  ① Importation Glisser-déposer   Aperçu des 5 premières    ✅ Présent
                un fichier CSV    lignes + statistiques     

  ② Mapping     Sélectionner      Validation type des       ✅ Présent
                User_ID / Item_ID colonnes                  
                / Rating                                    

  ③ Exploration Visualiser la     Heatmap, histogramme des  🆕 AJOUTÉ
                matrice et les    notes, sparsité           
                KPIs du dataset                             

  ④ Requête     Choisir un item   Calcul en temps réel avec ✅ Présent
                et définir N      spinner                   

  ⑤ Résultats   Consulter le      Tableau + graphique +     🔧 ENRICHI
                Top-N et les      export multi-format       
                métriques                                   
  ------------- ----------------- ------------------------- -------------------

# 4. Exigences Fonctionnelles

## 4.1. Module d'Importation de Données (F1) --- Enrichi

Fonctionnalités du CdC original :

-   Acceptation des fichiers .csv

-   Affichage d'un aperçu des 5 premières lignes du fichier

**🆕 Fonctionnalités ajoutées (obligatoires) :**

-   Validation automatique du fichier : encodage (UTF-8, Latin-1),
    délimiteur (virgule, point-virgule, tabulation), taille max
    configurable

-   Rapport de qualité des données : % de valeurs manquantes, doublons
    détectés, plage des ratings, nb d'utilisateurs et d'items distincts

-   Saisie manuelle item-par-item : en alternative au CSV, l'utilisateur
    peut entrer des triplets (user, item, rating) directement dans
    l'interface

-   Support futur (roadmap) : Excel .xlsx, JSON, connexion API REST

Pour maximiser l\'accessibilité et faciliter les démonstrations , le
système propose deux modes d\'ingestion de données

**Mode A : Importation par lot (Fichier)**\
▸ Acceptation des fichiers .csv par glisser-déposer.\
▸ Validation automatique : encodage, délimiteur, taille max.

**Mode B : Ingénierie manuelle (Saisie in-app)**\
▸ Intégration d\'un tableur interactif directement dans l\'interface web
(via st.data_editor).\
▸ L\'utilisateur peut saisir manuellement ses triplets (User, Item,
Rating) ligne par ligne, idéal pour des tests rapides, la validation de
l\'algorithme par le correcteur, ou la résolution du problème de
démarrage à froid (*Cold Start*).

**Fonctions communes aux deux modes :**\
▸ Rapport de qualité des données : % de valeurs manquantes, doublons
détectés, plage des ratings.\
▸ Standardisation en un DataFrame Pandas unique transmis au reste de
l\'application.

## 4.2. Mapping Dynamique des Variables (F2) --- Maintenu

Fonctionnalités du CdC original :

-   Extraction dynamique des noms de colonnes du fichier

-   3 menus déroulants obligatoires : User_ID, Item_ID, Rating

**🆕 Fonctionnalités ajoutées :**

-   Détection intelligente : le système propose automatiquement un
    mapping probable en analysant les noms de colonnes (ex : 'user',
    'userId', 'client' → User_ID)

-   Validation du type de données : si la colonne Rating contient des
    valeurs non numériques, affichage d'un avertissement clair et
    blocage du calcul

-   Normalisation des ratings : option pour normaliser les valeurs sur
    \[0, 1\] ou \[1, 5\] si l'échelle est hétérogène

## 4.3. Module d'Exploration des Données --- NOUVEAU (F2-bis)

+-----------------------------------------------------------------------+
| **🆕 Fonctionnalité absente du CdC original --- À intégrer            |
| impérativement**                                                      |
|                                                                       |
| Les meilleures plateformes SaaS d'analyse de données (Tableau, Power  |
| BI, Recombee) proposent systématiquement                              |
|                                                                       |
| un tableau de bord exploratoire avant le calcul algorithmique. Cette  |
| étape renforce la confiance de l'utilisateur.                         |
|                                                                       |
| Éléments à afficher :                                                 |
|                                                                       |
| • KPIs clés : nb utilisateurs, nb items, nb interactions, densité de  |
| la matrice (sparsité en %)                                            |
|                                                                       |
| • Distribution des ratings : histogramme des notes (Plotly)           |
|                                                                       |
| • Top 10 items les plus notés : bar chart horizontal                  |
|                                                                       |
| • Top 10 utilisateurs les plus actifs : bar chart horizontal          |
|                                                                       |
| • Heatmap de la matrice Utilisateurs × Items (sous-échantillonnée si  |
| trop grande)                                                          |
+-----------------------------------------------------------------------+

## 4.4. Moteur de Recommandation --- Cœur Algorithmique (F3) --- Enrichi

Fonctionnalités du CdC original :

-   Transformation en matrice Produits × Utilisateurs (Pivot Table)

-   Calcul de similarité Cosinus ou Pearson

-   Gestion des valeurs manquantes (remplacement par 0 ou moyenne de
    l'item)

**🆕 Fonctionnalités ajoutées :**

-   Choix de la métrique de similarité : menu déroulant Cosinus /
    Pearson avec explication pédagogique de chaque méthode

-   Seuil de similarité minimum : slider permettant de filtrer les items
    avec une similarité \< seuil (ex : exclure les items avec score \<
    0.1)

-   Filtre de popularité minimum : exclure les items notés par moins de
    K utilisateurs pour éviter les recommandations marginales

-   Mode multi-items : recommandation basée sur un panier de plusieurs
    items cibles (moyenne des vecteurs de similarité)

-   Explainability : pour chaque item recommandé, afficher les 3
    utilisateurs communs qui justifient la similarité

## 4.5. Interface de Restitution des Résultats (F4) --- Enrichi

Fonctionnalités du CdC original :

-   Menu déroulant listant tous les Item_ID

-   Curseur (Slider) pour définir N

-   Tableau des résultats avec nom et score de similarité

**🆕 Fonctionnalités ajoutées :**

-   Barre de recherche intelligente : saisie libre avec autocomplétion
    sur l'Item_ID (plus rapide qu'un dropdown avec des milliers d'items)

-   Visualisation graphique des résultats : bar chart horizontal du
    score de similarité des N items recommandés

-   Carte de chaleur de similarité : mini-heatmap comparant l'item cible
    avec les N items recommandés

-   Export multi-format : CSV, JSON, et rapport PDF auto-généré (avec
    logo + date + paramètres utilisés)

-   Bouton 'Recommander à nouveau' : reset rapide sans perdre le dataset
    chargé

-   Historique de session : liste déroulante des 5 dernières requêtes
    effectuées dans la session en cours

## 4.6. Tableau de Bord Principal --- NOUVEAU (F5)

+-----------------------------------------------------------------------+
| **🆕 Dashboard récapitulatif --- Bonne pratique SaaS 2025**           |
|                                                                       |
| Après le calcul, afficher un panneau de synthèse consolidé contenant  |
| :                                                                     |
|                                                                       |
| • Métriques du dataset : utilisateurs, items, interactions, sparsité  |
|                                                                       |
| • Paramètres utilisés : algorithme, métrique, seuil, N                |
|                                                                       |
| • Top-N actuel : tableau interactif avec tri par score                |
|                                                                       |
| • Graphique radar : comparaison du profil de rating de l'item cible   |
| vs items recommandés                                                  |
|                                                                       |
| • Statut du cache : indicateur visuel si la matrice est déjà calculée |
| (évite le re-calcul)                                                  |
+-----------------------------------------------------------------------+

# 5. Exigences Non-Fonctionnelles

## 5.1. Robustesse & Gestion des Erreurs --- Enrichi

  ------------------------ ------------------------------ ----------------
  **Scénario d'Erreur**    **Comportement Attendu**       **Priorité**

  Colonnes mal mappées     Message d'erreur en rouge +    CRITIQUE
                           guide de correction            

  Rating non numérique     Blocage du calcul + liste des  CRITIQUE
                           lignes problématiques          

  Fichier trop volumineux  Warning + recommandation de    HAUTE
  (\> 50 MB)               sous-échantillonner            

                                                          

  Item cible sans aucune   Message explicatif +           HAUTE
  note                     suggestion d'items alternatifs 

  Encodage de fichier      Détection auto + proposition   MOYENNE
  incorrect                de ré-encodage                 

  Valeur N supérieure au   Ajustement automatique de N +  MOYENNE
  nb d'items               notification                   
  ------------------------ ------------------------------ ----------------

## 5.2. Performance & Mise en Cache --- Enrichi

-   Indicateur de chargement visuel (spinner animé) pendant le calcul de
    la matrice de similarité

-   Mise en cache de la matrice de similarité complète avec
    st.cache_data : aucun re-calcul si le dataset n'a pas changé

-   Hash de fichier : le cache est invalidé automatiquement si un
    nouveau fichier est uploadé

-   🆕 Calcul progressif : pour les grands datasets (\> 10 000 items),
    affichage d'une barre de progression avec pourcentage

-   🆕 Avertissement de taille : si le dataset dépasse 100 000 lignes,
    proposer un mode rapide avec sous-échantillonnage aléatoire
    stratifié

## 5.3. UX / Ergonomie --- Enrichi

-   Interface épurée, claire, compréhensible par un non-expert en Data
    Science

-   Police Satori importée via Google Fonts dans le thème Streamlit

-   🆕 Mode sombre / clair : toggle en haut à droite, respectant les
    préférences système

-   🆕 Guide intégré (Onboarding Tooltip) : icônes d'aide '?' à côté de
    chaque paramètre technique (ex : explication de la similarité
    cosinus en langage simple)

-   🆕 Sidebar de navigation : menu latéral pour naviguer entre les
    sections (Import, Exploration, Recommandation, Export)

-   🆕 Responsive design : interface testée sur desktop (1920px), laptop
    (1366px) et tablette (768px)

-   🆕 Internationalisation (i18n) : support Français / Anglais via un
    toggle de langue en header

## 5.4. Sécurité & Confidentialité des Données --- NOUVEAU

+-----------------------------------------------------------------------+
| **🆕 Exigences absentes du CdC original --- Essentielles pour un SaaS |
| professionnel**                                                       |
|                                                                       |
| • Les fichiers uploadés sont traités exclusivement en mémoire RAM     |
| (session Streamlit) --- aucune persistance sur disque.                |
|                                                                       |
| • Aucune donnée utilisateur n'est transmise à des services tiers non  |
| explicitement mentionnés.                                             |
|                                                                       |
| • Avertissement RGPD affiché lors de l'upload : 'Vos données restent  |
| confidentielles et sont supprimées à la fermeture de la session.'     |
|                                                                       |
| • 🆕 Anonymisation optionnelle : masquer les User_ID dans les         |
| visualisations (remplacer par User_001, User_002\...)                 |
|                                                                       |
| • 🆕 Limite sur les données sensibles : recommandation de ne pas      |
| uploader de données nominatives (RGPD compliance).                    |
+-----------------------------------------------------------------------+

## 5.5. Métriques de Qualité Algorithmique --- NOUVEAU

+-----------------------------------------------------------------------+
| **🆕 Section absente --- Valeur ajoutée pédagogique et                |
| professionnelle significative**                                       |
|                                                                       |
| Afficher automatiquement les métriques d'évaluation du modèle         |
| (calculées sur un split test 80/20) :                                 |
|                                                                       |
| • Précision@N (Precision at N) : % des items recommandés réellement   |
| pertinents                                                            |
|                                                                       |
| • Couverture (Coverage) : % du catalogue total que le moteur est      |
| capable de recommander                                                |
|                                                                       |
| • Diversité intra-liste : mesure de la dissimilarité entre les N      |
| items recommandés                                                     |
|                                                                       |
| • Taux de popularité : éviter le biais vers les items                 |
| ultra-populaires (longue traîne)                                      |
|                                                                       |
| Ces métriques sont affichées dans un encadré dédié après chaque       |
| recommandation.                                                       |
+-----------------------------------------------------------------------+

# 6. Architecture Technique

## 6.1. Structure des Fichiers

L'application sera organisée selon l'architecture modulaire suivante :

## 6.2. Stack Technologique

  ---------------- ------------------------ ------------------------------
  **Couche**       **Technologie**          **Usage**

  Frontend         Streamlit 1.35+          Interface web, widgets,
                                            navigation

  Calcul matriciel NumPy + Pandas           Pivot table, similarité from
                                            scratch

  Visualisation    Plotly Express           Graphiques interactifs
                                            (heatmap, barplot)

  Export PDF       FPDF2                    Rapport PDF auto-généré

  Hébergement      Streamlit Community      URL publique, déploiement
                   Cloud                    GitHub

  CI/CD            GitHub Actions           Tests automatiques à chaque
                   (optionnel)              push
  ---------------- ------------------------ ------------------------------

# 7. Livrables Attendus

  --------------------- --------------------------------- ----------------
  **Livrable**          **Description**                   **Statut**

  Code Source Python    Fichiers .py commentés PEP8,      Obligatoire
                        structurés en modules             

  Application Déployée  URL publique Streamlit Cloud      Obligatoire
                        fonctionnelle                     

  Dataset de démo       Extrait MovieLens 100K (CSV prêt  Obligatoire
                        à tester)                         

  README.md             Guide d'installation,             Obligatoire
                        d'utilisation et lien URL         

  Rapport PDF           Export PDF in-app avec logo,      🆕 Ajouté
  auto-généré           paramètres, résultats             

  Métriques             Precision@N, Coverage, Diversity  🆕 Ajouté
  d'évaluation          affichées in-app                  

  Tests unitaires       Test des fonctions de similarité  🆕 Recommandé
                        (pytest)                          
  --------------------- --------------------------------- ----------------

# 9. Critères d'Évaluation et Points Différenciants

+-----------------------------------------------------------------------+
| **🏆 Ce qui fera la différence face aux autres rendus**               |
|                                                                       |
| 1\. Algorithme rigoureusement from scratch (aucune lib ML) avec       |
| démonstration mathématique dans l'UI                                  |
|                                                                       |
| 2\. Tableau de bord d'exploration des données (EDA) intégré avant le  |
| calcul                                                                |
|                                                                       |
| 3\. Métriques de qualité algorithmique calculées et affichées         |
| (Precision@N, Coverage, Diversity)                                    |
|                                                                       |
| 4\. Export PDF professionnel auto-généré avec paramètres et résultats |
|                                                                       |
| 5\. Explainability : justification des recommandations par les        |
| utilisateurs communs                                                  |
|                                                                       |
| 6\. UX soignée : police Satori, mode sombre, guide d'aide intégré,    |
| sidebar de navigation                                                 |
|                                                                       |
| 7\. Sécurité RGPD : traitement en mémoire uniquement, avertissement   |
| utilisateur                                                           |
|                                                                       |
| 8\. Performance : cache intelligent avec invalidation par hash de     |
| fichier                                                               |
+-----------------------------------------------------------------------+

*--- Fin du Cahier des Charges v2.0 ---*
