# RecoSaaS — Planning Agile par Sprints

**Projet** : Plateforme SaaS de Recommandation Intelligente (Filtrage Collaboratif Item-Item)
**Cadre** : TP1 — Big Data / Machine Learning
**Document source** : `CDC_RecoSaaS_v2.md` (v2.0 — 05 Mai 2026)
**Version planning** : 1.0
**Date** : 05 Mai 2026

---

## Préambule — Contraintes structurantes

1. **Algorithme from scratch obligatoire** : interdiction d'utiliser `scikit-learn`, `surprise`, `implicit`, ou tout package de filtrage collaboratif. Tout calcul de similarité (Cosinus / Pearson) est codé à la main avec `pandas` et `numpy` exclusivement.
2. **Séparation Back / Front stricte** : la logique métier (`core/`) ne doit jamais importer `streamlit`. Elle reste testable, réutilisable et déployable indépendamment.
3. **Architecture bimodale dès le Sprint 1** : Mode A (Upload CSV) et Mode B (Saisie Manuelle via `st.data_editor`) cohabitent et alimentent un DataFrame standardisé unique.
4. **Contrat de données figé** : toute la chaîne consomme un DataFrame à 3 colonnes `[user_id, item_id, rating]`.
5. **Pas de persistance disque** : tout vit en RAM (`BytesIO` + `st.session_state`) — exigence RGPD du CDC §5.4.

---

## Sprint 0 — Initialisation & Architecture du Projet

**Objectif principal** : Mettre en place le squelette technique modulaire, isoler dès le départ le Back-end (logique pure) du Front-end (Streamlit), et garantir une base propre pour tout le reste.

### Tickets / Tâches

**Setup**
- `SETUP-01` : Créer le dépôt GitHub, ajouter `.gitignore` (Python, `.streamlit/`, `__pycache__/`), `LICENSE`, `README.md` initial.
- `SETUP-02` : Initialiser l'environnement Python 3.10+ avec `venv` ou `poetry`. Geler les versions dans `requirements.txt` (`streamlit>=1.35`, `pandas`, `numpy`, `plotly`, `fpdf2`, `pytest`).
- `SETUP-03` : Créer la structure modulaire :

```text
recosaas/
├── app.py                  # Point d'entrée Streamlit (router pages)
├── core/                   # Back-end pur (testable sans Streamlit)
│   ├── __init__.py
│   ├── ingestion.py        # Lecture CSV + Saisie manuelle
│   ├── validation.py       # Qualité données, types, encodages
│   ├── mapping.py          # Détection colonnes, normalisation
│   ├── matrix.py           # Pivot User × Item
│   ├── similarity.py       # Cosinus, Pearson FROM SCRATCH
│   ├── recommender.py      # Top-N, filtres, multi-items
│   ├── metrics.py          # Precision@N, Coverage, Diversity
│   └── exporter.py         # CSV, JSON, PDF
├── ui/                     # Front-end Streamlit
│   ├── pages/
│   ├── components/         # Widgets réutilisables
│   ├── theme.py            # Police Satori, dark mode
│   └── i18n/               # fr.json, en.json
├── tests/                  # pytest sur core/ uniquement
├── data/sample/            # MovieLens 100k extrait
└── .streamlit/config.toml
```

- `SETUP-04` : Configurer `.streamlit/config.toml` (thème de base, layout `wide`).
- `SETUP-05` : Workflow GitHub Actions minimal (lint `ruff` + `pytest`) — optionnel mais recommandé.

### Points d'attention techniques (Lead Tech)

- **Règle d'or** : aucun import de `streamlit` dans `core/`. C'est la clé pour rester testable et éviter le couplage. Les fonctions de `core/` retournent des `DataFrame` / `np.ndarray` / `dict`, jamais des widgets.
- **Pas encore de logique** : ce sprint sert à éviter le syndrome du "fichier Python de 1500 lignes" qu'on voit dans 80 % des TP.
- **Convention** : nommer les fonctions du `core/` au présent impératif (`compute_similarity`, `build_pivot_matrix`) — aucun verbe lié à l'UI.
- Anticiper l'absence de scikit-learn : ajouter une note dans `requirements.txt` interdisant `sklearn`, `surprise`, `implicit`.

### Definition of Done

- Le projet se lance avec `streamlit run app.py` et affiche une page blanche "Hello RecoSaaS".
- `pytest` tourne (même sans tests réels).
- Le repo GitHub est public, le README contient le plan des sprints.

---

## Sprint 1 — Ingestion Bimodale & Standardisation des Données

**Objectif principal** : Implémenter dès maintenant les **deux modes d'ingestion** (Mode A — Upload CSV / Mode B — Saisie Manuelle via `st.data_editor`) car cette dualité conditionne toute l'architecture des `session_state` qui suivent.

### Tickets / Tâches

**Back-end (`core/ingestion.py`, `core/validation.py`)**
- `BACK-11` : Fonction `load_csv(file_buffer) -> pd.DataFrame` avec auto-détection de l'encodage (`utf-8` puis fallback `latin-1`) et du séparateur (`,`, `;`, `\t`) via `pd.read_csv(sep=None, engine='python')`.
- `BACK-12` : Fonction `validate_file_size(file, max_mb=50) -> dict` retournant `{ok: bool, warnings: [...]}`.
- `BACK-13` : Fonction `build_manual_dataframe(rows: list[dict]) -> pd.DataFrame` qui standardise une saisie manuelle au même schéma que le CSV.
- `BACK-14` : Fonction `standardize(df, user_col, item_col, rating_col) -> pd.DataFrame` retournant **toujours** un DataFrame à 3 colonnes `[user_id, item_id, rating]` (le contrat unique pour le reste du pipeline).

**Front-end (`ui/pages/01_import.py`)**
- `FRONT-11` : Page "Importation" avec un `st.radio("Mode d'ingestion", ["Fichier CSV", "Saisie manuelle"])`.
- `FRONT-12` : Mode A — `st.file_uploader` (drag & drop), aperçu `st.dataframe(df.head())`, badge taille fichier.
- `FRONT-13` : Mode B — `st.data_editor` avec un DataFrame template `[user_id, item_id, rating]` et `num_rows="dynamic"`, plus un bouton "Charger un exemple cold-start" qui pré-remplit 10 lignes.
- `FRONT-14` : Stocker le DataFrame standardisé dans `st.session_state["raw_df"]` quel que soit le mode choisi.
- `FRONT-15` : Avertissement RGPD visible sur cette page (`st.info`).

### Points d'attention techniques (Lead Tech)

- **`st.session_state` est ton seul allié** contre les re-runs intempestifs de Streamlit. À la fin du Sprint 1, **toute donnée transverse doit y vivre** : `raw_df`, `ingestion_mode`, `file_hash`.
- Pour le hash du fichier (qui servira au cache du Sprint 4), calculer `hashlib.md5(file.getvalue()).hexdigest()` dès l'upload — pas plus tard.
- `st.data_editor` : forcer les `column_config` (NumberColumn pour `rating` avec `min_value`, `max_value`) sinon l'utilisateur entre du texte et tu débugges 2h.
- **Ne JAMAIS écrire le fichier sur disque** (exigence 5.4 du CDC). Tout reste en RAM via `BytesIO`.
- Le contrat de sortie `[user_id, item_id, rating]` doit être figé dès maintenant — c'est le point de jonction Back/Front pour 100 % du reste.

### Definition of Done

- L'utilisateur peut basculer entre Upload CSV et Saisie Manuelle sans perdre l'état des autres pages.
- Le DataFrame standardisé `st.session_state["raw_df"]` existe avec exactement 3 colonnes après la page d'import, dans les deux modes.
- Le dataset MovieLens 100k de démo se charge en moins de 2 secondes.
- Aucun fichier ne touche le disque.

---

## Sprint 2 — Mapping Dynamique & Rapport Qualité

**Objectif principal** : Couvrir F2 (mapping intelligent) et la partie "Rapport de qualité" de F1, avec gestion d'erreurs critiques (CDC §5.1 priorité CRITIQUE).

### Tickets / Tâches

**Back-end (`core/mapping.py`, `core/validation.py`)**
- `BACK-21` : `suggest_mapping(columns: list[str]) -> dict` — heuristique par regex (`r"user|client|customer|uid"` → `user_id`, etc.), insensible à la casse.
- `BACK-22` : `validate_rating_column(series) -> dict` retournant `{ok, n_invalid, invalid_indices, dtype}`.
- `BACK-23` : `quality_report(df) -> dict` calculant : `n_users`, `n_items`, `n_interactions`, `pct_missing`, `n_duplicates`, `rating_min/max/mean`, `sparsity`.
- `BACK-24` : `normalize_ratings(series, scale="0-1" | "1-5") -> series` (transformation min-max simple, pure NumPy).

**Front-end (`ui/pages/02_mapping.py`)**
- `FRONT-21` : 3 `st.selectbox` (User_ID, Item_ID, Rating) pré-remplis par la suggestion automatique.
- `FRONT-22` : `st.metric` x4 affichant le rapport qualité (densité, doublons, NaN, plage ratings).
- `FRONT-23` : Si `validate_rating_column().ok == False` → `st.error` avec extrait des lignes fautives (`df.iloc[invalid_indices].head(10)`) + bouton "Bloquer le calcul" désactivé.
- `FRONT-24` : `st.toggle("Normaliser les ratings")` avec `st.radio` pour le choix d'échelle.
- `FRONT-25` : Stocker `st.session_state["clean_df"]` une fois la validation passée.

### Points d'attention techniques (Lead Tech)

- La détection automatique doit rester **best-effort** : afficher les suggestions dans les `selectbox` mais laisser la main à l'utilisateur. Ne jamais cacher l'option.
- `pd.to_numeric(series, errors="coerce")` pour le contrôle de type — les `NaN` apparus signalent les lignes fautives.
- La sparsité se calcule simplement : `1 - (n_interactions / (n_users * n_items))`. Pas besoin de matrice à ce stade.
- Bien séparer `raw_df` (sortie du Sprint 1) et `clean_df` (sortie du Sprint 2). Ne jamais muter en place.

### Definition of Done

- Les colonnes sont mappées soit auto, soit manuellement, et la suggestion fonctionne sur ≥ 3 datasets différents (MovieLens, un dataset e-commerce, un dataset RH fictif).
- Les 6 scénarios d'erreur du tableau §5.1 du CDC sont couverts pour ce qui concerne le mapping et le rating non numérique.
- Le rapport qualité s'affiche en moins d'une seconde sur MovieLens 100k.

---

## Sprint 3 — Module d'Exploration des Données (EDA)

**Objectif principal** : Construire le tableau de bord exploratoire F2-bis (nouveauté du CDC v2.0) — c'est un point différenciant explicite du §9.

### Tickets / Tâches

**Back-end (`core/eda.py`, à créer)**
- `BACK-31` : `compute_kpis(clean_df) -> dict` (n_users, n_items, sparsité, etc.).
- `BACK-32` : `top_k_items(clean_df, k=10) -> pd.Series` (basé sur `value_counts`).
- `BACK-33` : `top_k_users(clean_df, k=10) -> pd.Series`.
- `BACK-34` : `subsample_pivot_for_heatmap(clean_df, max_users=50, max_items=50) -> pd.DataFrame` — tirage stratifié par activité (top users × top items).

**Front-end (`ui/pages/03_exploration.py`)**
- `FRONT-31` : 4 `st.metric` en colonnes pour les KPIs (utilisateurs, items, interactions, sparsité %).
- `FRONT-32` : Histogramme des notes (`plotly.express.histogram` sur `rating`).
- `FRONT-33` : Bar chart horizontal Top 10 items (`px.bar(orientation='h')`).
- `FRONT-34` : Bar chart horizontal Top 10 users.
- `FRONT-35` : Heatmap `px.imshow` de la matrice sous-échantillonnée, avec `st.caption` qui prévient explicitement quand le sous-échantillonnage a eu lieu.

### Points d'attention techniques (Lead Tech)

- **Heatmap = piège classique** : sur MovieLens 100k, une matrice 943 × 1682 = 1.5 M de cellules tue le navigateur. Le sous-échantillonnage stratifié (top-N users × top-N items) est non négociable.
- Toujours passer par Plotly Express pour la cohérence visuelle (un seul moteur graphique sur tout le projet).
- Mettre les résultats lourds (top_k, kpis) en cache : `@st.cache_data` avec en argument le `file_hash` (Sprint 1) — pas le DataFrame, qui n'est pas hashable nativement et ralentit le cache.
- Déjà préparer la **sidebar de navigation** (CDC §5.3) avec `st.sidebar` ou `st.navigation` (Streamlit 1.36+).

### Definition of Done

- La page Exploration affiche les 5 visualisations sans erreur sur MovieLens 100k en moins de 3 secondes.
- Aucun re-calcul si l'utilisateur navigue puis revient sur la page (vérifié via `print` dans la fonction cachée).
- L'utilisateur n'a strictement rien à coder pour explorer son dataset.

---

## Sprint 4 — Cœur Algorithmique from Scratch (Pivot + Similarité)

**Objectif principal** : Implémenter le moteur F3 *cœur* avec **interdiction stricte** d'utiliser `sklearn.metrics.pairwise`, `scipy.spatial.distance`, ou tout package de filtrage collaboratif. Ce sprint est le pivot du projet — il sera challengé par le correcteur.

### Tickets / Tâches

**Back-end (`core/matrix.py`, `core/similarity.py`)**
- `ALGO-41` : `build_pivot_matrix(clean_df) -> pd.DataFrame` via `df.pivot_table(index='item_id', columns='user_id', values='rating')`. **Items en lignes** (orientation Item-Item).
- `ALGO-42` : `cosine_similarity_matrix(matrix: np.ndarray) -> np.ndarray` from scratch :
  - Remplir les NaN par 0 (cosinus traite l'absence comme "non noté = neutre").
  - Calculer `norms = np.linalg.norm(matrix, axis=1)`.
  - Retourner `(matrix @ matrix.T) / np.outer(norms, norms)`, avec gestion des divisions par zéro (`np.where`).
- `ALGO-43` : `pearson_similarity_matrix(matrix: np.ndarray) -> np.ndarray` from scratch :
  - **Centrer chaque ligne** par la moyenne des notes existantes (sans compter les NaN) : `centered = matrix - np.nanmean(matrix, axis=1, keepdims=True)`.
  - Remplacer les NaN par 0 *après* centrage uniquement.
  - Reprendre la formule cosinus sur la matrice centrée → équivaut à Pearson.
- `ALGO-44` : Fonction `build_similarity_matrix(pivot, metric)` dispatcher.
- `ALGO-45` : Mise en cache via `@st.cache_data(show_spinner=False)` clée sur `(file_hash, metric)`.

**Tests (`tests/test_similarity.py`)**
- `TEST-41` : Cas trivial 3×3 calculé à la main → assert valeurs cosinus à 6 décimales.
- `TEST-42` : Cas Pearson avec un utilisateur "généreux" (notes toujours hautes) — la similarité Pearson doit être insensible au biais utilisateur, pas la cosinus. C'est le test pédagogique qui valide la qualité du from-scratch.
- `TEST-43` : Symétrie : `S == S.T` (à `1e-10` près).
- `TEST-44` : Diagonale = 1 (un item est parfaitement similaire à lui-même).

**Front-end (`ui/pages/04_recommandation.py` — squelette uniquement)**
- `FRONT-41` : `st.selectbox("Métrique", ["Cosinus", "Pearson"])` avec `st.expander` "Comprendre la différence" (pédagogie).
- `FRONT-42` : `st.button("Calculer la matrice")` qui déclenche l'algo, suivi d'un `st.success("Matrice prête")` avec dimensions affichées.

### Points d'attention techniques (Lead Tech)

- **Vectorisation absolue** : aucune boucle `for i in items: for j in items:`. Sur 1682 items, une double boucle Python = 4 minutes ; un produit matriciel NumPy = 0.2 seconde. Si tu écris une boucle ici, c'est rouge.
- **Pearson est un piège** : 90 % des étudiants soustraient la moyenne **après** avoir mis les NaN à 0 → ils calculent une moyenne biaisée par les zéros artificiels. Toujours `np.nanmean` puis remplacement.
- `np.linalg.norm` peut renvoyer 0 → diviser génère `NaN`/`inf`. Toujours `np.where(norms == 0, 1, norms)` avant la division puis remettre 0 à la fin.
- La matrice de similarité Items × Items pour MovieLens 1682×1682 = 22 Mo en `float64`. C'est OK. Au-delà de 50 k items, prévoir `float32` (mais hors périmètre TP).
- **Stocker la matrice de similarité dans `st.session_state["sim_matrix"]`** + un mapping `item_id → index` pour les lookups ultérieurs.

### Definition of Done

- La matrice de similarité est calculée pour MovieLens 100k en moins de 2 secondes.
- Les 4 tests unitaires passent.
- Un re-clic sur "Calculer" ne re-déclenche pas le calcul (cache hit visible dans les logs).
- Aucun import de bibliothèque ML interdite (vérifiable avec `grep "import sklearn"`).

---

## Sprint 5 — Moteur de Recommandation Avancé

**Objectif principal** : Compléter F3 avec toutes les fonctionnalités enrichies du CDC v2.0 : seuil de similarité, filtre de popularité, mode multi-items, et **explainability**.

### Tickets / Tâches

**Back-end (`core/recommender.py`)**
- `BACK-51` : `recommend_top_n(sim_matrix, item_index, n, threshold, min_popularity, popularity_series) -> pd.DataFrame` :
  1. Récupérer la ligne de similarité de l'item cible.
  2. Filtrer par `popularity >= min_popularity`.
  3. Filtrer par `score >= threshold`.
  4. Retirer l'item lui-même.
  5. Trier décroissant et retourner top N avec colonnes `[item_id, similarity_score, popularity]`.
- `BACK-52` : `recommend_multi_items(sim_matrix, item_indices, n, ...) -> pd.DataFrame` — moyenne des vecteurs de similarité (`sim_matrix[indices].mean(axis=0)`), puis exclusion des items du panier.
- `BACK-53` : `explain_recommendation(clean_df, target_item, recommended_item, top_k_users=3) -> list[dict]` — retourner les 3 utilisateurs ayant noté les deux items, avec leurs deux notes (justification visuelle).
- `BACK-54` : `compute_item_popularity(clean_df) -> pd.Series` (counts par item).

**Front-end (`ui/pages/04_recommandation.py`)**
- `FRONT-51` : Recherche autocomplétée — utiliser `st.selectbox` avec la liste filtrée (Streamlit gère la recherche fuzzy nativement) ; alternativement `streamlit-searchbox` si plus pertinent UX.
- `FRONT-52` : Slider N (`st.slider(min=1, max=20, value=5)`).
- `FRONT-53` : Slider seuil de similarité (`0.0 → 1.0`, step `0.05`).
- `FRONT-54` : `st.number_input` filtre popularité (notations minimales).
- `FRONT-55` : `st.multiselect("Mode panier (multi-items)")` activé par toggle.
- `FRONT-56` : Pour chaque item recommandé, un `st.expander("Pourquoi cet item ?")` qui appelle `explain_recommendation` et affiche un mini-tableau des 3 users communs.
- `FRONT-57` : Gestion du cas "item cible sans aucune note" → `st.warning` + suggestion d'alternatives (top items populaires).

### Points d'attention techniques (Lead Tech)

- **Item index ≠ item_id** : maintenir un mapping `item_id_to_index` et `index_to_item_id` dans `session_state` dès la création du pivot. Toutes les opérations vectorisées travaillent sur les index.
- L'auto-exclusion de l'item cible est facile à oublier — toujours `mask[item_index] = False` avant le tri.
- En multi-items, soustraire **tous** les items du panier dans le résultat, sinon recommander un item à lui-même.
- L'explainability doit rester rapide : `df[(df.item_id == A) | (df.item_id == B)].pivot(...)` puis `dropna()` pour récupérer les users communs. Sur MovieLens, ça reste sous 50 ms.
- Mettre l'historique des 5 dernières requêtes dans `st.session_state["query_history"] = collections.deque(maxlen=5)`.

### Definition of Done

- L'utilisateur obtient un Top-N filtré par seuil et popularité, avec explainability fonctionnelle.
- Le mode multi-items génère des recommandations cohérentes (validé sur le panier "Toy Story + Star Wars" → recommande des familles/SF).
- L'historique de session affiche les 5 dernières requêtes avec leur paramétrage.
- Tous les scénarios d'erreur §5.1 sont couverts (item sans note, N > nb items).

---

## Sprint 6 — Restitution Visuelle, Évaluation & Dashboard Récapitulatif

**Objectif principal** : Couvrir F4 enrichi, F5 (dashboard), et la grosse pièce différenciante §5.5 (métriques de qualité algorithmique).

### Tickets / Tâches

**Back-end (`core/metrics.py`)**
- `BACK-61` : `train_test_split_per_user(clean_df, test_ratio=0.2, seed=42) -> (train_df, test_df)` — split stratifié *par user* (sinon des users du test sont absents du train, c'est mathématiquement faux).
- `BACK-62` : `precision_at_n(recommender_fn, train_df, test_df, n=5) -> float` — pour chaque user du test, item "vu" en test = pertinent si dans le top-N de recommandations. Retourner la moyenne.
- `BACK-63` : `coverage(recommender_fn, items, n=5) -> float` — % d'items du catalogue qui apparaissent au moins une fois dans une recommandation top-N (sur un échantillon d'items cibles).
- `BACK-64` : `intra_list_diversity(recommended_items, sim_matrix) -> float` — `1 - moyenne(sim(i,j))` pour `i,j` dans la liste recommandée.
- `BACK-65` : `popularity_bias(recommended_items, popularity_series) -> float`.

**Front-end (`ui/pages/05_dashboard.py`)**
- `FRONT-61` : Bar chart horizontal Plotly du score des N items recommandés.
- `FRONT-62` : Mini-heatmap de similarité Item cible × Items recommandés (`px.imshow` sur une slice de `sim_matrix`).
- `FRONT-63` : Graphique radar (`go.Scatterpolar`) comparant le profil de notation moyen de l'item cible vs profils moyens des recommandés (par tranche de rating, ou par décile d'utilisateurs).
- `FRONT-64` : Encadré "Qualité du modèle" avec 4 `st.metric` (Precision@N, Coverage, Diversity, Popularity Bias).
- `FRONT-65` : Tableau de synthèse des paramètres utilisés (`metric`, `threshold`, `min_pop`, `N`) en `st.dataframe`.
- `FRONT-66` : Indicateur statut cache (`st.success` ou `st.info`) selon `cache_hit`.

### Points d'attention techniques (Lead Tech)

- **Le calcul des métriques est coûteux** (boucle sur tous les users du test). Le mettre derrière un `st.button("Évaluer le modèle")` séparé et le cacher avec `@st.cache_data` clé sur `(file_hash, metric, threshold, min_pop, n)`.
- Pour `coverage` sur grands datasets, échantillonner 200 items cibles aléatoires plutôt que tout le catalogue — sinon on attend 5 minutes.
- Le radar exige des axes communs : normaliser les profils sur 5 tranches `[1-2, 2-3, 3-4, 4-5, 5]` et plot `% de notes dans chaque tranche`.
- Évaluation = données distinctes du calcul de production. Recalculer `sim_matrix` sur `train_df` uniquement pour cette section, sinon biais d'évaluation (data leakage).

### Definition of Done

- Le dashboard affiche tous les éléments F5 sur une seule page scrollable.
- Les 4 métriques de qualité s'affichent en moins de 10 secondes sur MovieLens 100k.
- Le radar est lisible (au moins 3 axes, pas vide).
- Le statut du cache change visuellement après le premier calcul.

---

## Sprint 7 — UX Premium, Sécurité & Internationalisation

**Objectif principal** : Tous les éléments §5.3 et §5.4 du CDC qui transforment un TP en SaaS — c'est ce qui différencie au correctif.

### Tickets / Tâches

**Front-end (`ui/theme.py`, `ui/i18n/`)**
- `FRONT-71` : Importer la police **Satori** via Google Fonts dans `.streamlit/config.toml` ou en injectant un `<link>` dans `st.markdown(unsafe_allow_html=True)`.
- `FRONT-72` : Toggle dark/light mode (`st.toggle("Mode sombre")`) avec persistance dans `session_state`. Streamlit 1.35+ supporte les thèmes dynamiques via `st.context.theme`.
- `FRONT-73` : Système i18n maison : deux fichiers JSON (`fr.json`, `en.json`), une fonction `t(key)` qui lit `st.session_state.lang`. Pas besoin de `gettext`, ce serait disproportionné.
- `FRONT-74` : Toggle de langue dans le header (icône drapeau).
- `FRONT-75` : Sidebar de navigation avec icônes pour les 5 pages (Import, Mapping, Exploration, Reco, Dashboard).
- `FRONT-76` : Tooltips d'aide `?` à côté des paramètres techniques — utiliser `help=` dans les widgets Streamlit (gratuit) plus pour les explications longues, des `st.popover`.
- `FRONT-77` : Tester en responsive (DevTools 1920/1366/768 px) — utiliser `st.columns` plutôt que CSS custom.

**Sécurité**
- `SEC-71` : Avertissement RGPD en `st.toast` au premier upload de la session.
- `SEC-72` : Toggle "Anonymiser les User_ID" qui remplace dans toutes les vues `user_42` par `User_001`, `User_002` (mapping en `session_state`, jamais persisté).
- `SEC-73` : Vérifier que `tempfile` n'est utilisé nulle part — uniquement `BytesIO`.

### Points d'attention techniques (Lead Tech)

- **Satori** : si la police est lourde, charger uniquement les graisses utilisées (400, 600). `<link>` dans le head évite le FOUT.
- L'i18n doit couvrir **tous les libellés statiques** dès maintenant, pas après. Sinon refacto pénible. Convention : aucun string hardcodé en français dans `ui/`, tout passe par `t("page.import.title")`.
- Le mode sombre via Streamlit reste limité aux composants natifs ; pour Plotly, switcher entre `template="plotly_white"` et `"plotly_dark"` selon `session_state.theme`.
- L'anonymisation se fait **à l'affichage** uniquement, jamais sur `clean_df`. Sinon les calculs deviennent incohérents entre sessions.

### Definition of Done

- L'interface est utilisable en français ET en anglais.
- Le mode sombre est cohérent (Streamlit + Plotly + tableaux).
- L'avertissement RGPD apparaît au premier upload.
- L'app reste lisible sur viewport 768 px.
- Police Satori visible (vérifiable au DevTools).

---

## Sprint 8 — Export PDF, Performance, Tests, Déploiement

**Objectif principal** : Boucler les livrables §7 du CDC (PDF auto-généré, tests, déploiement Streamlit Cloud) et finaliser le cache intelligent §5.2.

### Tickets / Tâches

**Back-end (`core/exporter.py`)**
- `BACK-81` : `export_csv(top_n_df) -> bytes` (trivial, `to_csv()`).
- `BACK-82` : `export_json(top_n_df, params) -> bytes`.
- `BACK-83` : `export_pdf(top_n_df, params, kpis, charts_as_png) -> bytes` avec **FPDF2** :
  - En-tête avec logo (générer un logo simple en SVG/PNG à inclure).
  - Date, paramètres (métrique, N, seuil, popularité).
  - Tableau Top-N.
  - Encadré métriques de qualité.
  - Footer "Généré par RecoSaaS — vos données restent confidentielles".

**Performance & Cache**
- `PERF-81` : Audit complet : chaque fonction lourde a-t-elle son `@st.cache_data` ? Vérifier avec `print` que MovieLens 100k → second appel < 100 ms.
- `PERF-82` : Barre de progression `st.progress` lors du calcul de la matrice si `n_items > 5000`.
- `PERF-83` : Sous-échantillonnage stratifié (`groupby('user_id').sample(frac=0.5)`) si `n_interactions > 100 000`, avec `st.warning` explicite et toggle pour le désactiver.

**Tests & Qualité**
- `TEST-81` : Tests unitaires sur `core/recommender.py` (top-N déterministe, exclusion item cible, multi-items).
- `TEST-82` : Tests sur `core/metrics.py` (precision sur dataset jouet où le résultat est calculable à la main).
- `TEST-83` : Linting `ruff check .` propre, `black --check`.

**Déploiement**
- `DEPLOY-81` : Pousser sur `main`, connecter à Streamlit Community Cloud.
- `DEPLOY-82` : Vérifier que `requirements.txt` est figé.
- `DEPLOY-83` : Tester l'URL publique sur 3 datasets différents.
- `DEPLOY-84` : Compléter le `README.md` (capture d'écran, lien public, comment lancer en local, structure du code, choix techniques justifiés vs scikit-learn).

### Points d'attention techniques (Lead Tech)

- **FPDF2** ne lit pas Plotly — il faut convertir les charts en PNG via `fig.to_image(format="png")` (nécessite `kaleido` dans `requirements.txt`).
- Sur Streamlit Cloud, `kaleido` peut être lourd : si problème, retomber sur `matplotlib` pour les exports PDF uniquement (conserver Plotly pour l'UI).
- Le cache `@st.cache_data` invalide automatiquement si l'argument change ; mais **attention** : il sérialise les retours, donc des objets non-picklables (ex: figures Plotly contenant des callbacks) cassent. Cacher uniquement les structures de données pures (`np.ndarray`, `pd.DataFrame`, `dict`).
- Streamlit Cloud limite à 1 GB de RAM en gratuit. Sur des datasets > 200k lignes, prévoir un message qui propose le sous-échantillonnage *avant* l'OOM.
- README : un correcteur passera 5 minutes dessus. Y mettre **dès le haut** : 1) lien URL public, 2) capture d'écran, 3) note "Aucune lib ML utilisée — voir `core/similarity.py`".

### Definition of Done

- L'utilisateur peut télécharger ses résultats en CSV, JSON et PDF (le PDF contient logo, paramètres, top-N et métriques).
- L'app est déployée sur une URL publique Streamlit Cloud accessible.
- `pytest` passe à 100 % avec ≥ 10 tests couvrant les fonctions critiques.
- Le `README.md` permet à un évaluateur de tout reproduire en moins de 5 minutes.
- Aucun re-calcul inutile lors d'une session normale (vérifié manuellement).

---

## Synthèse — Vue d'ensemble du planning

| Sprint | Thème | Charge estimée | Risque |
|---|---|---|---|
| 0 | Architecture & Setup | 0.5 j | Faible |
| 1 | Ingestion bimodale | 1.5 j | Moyen (st.data_editor) |
| 2 | Mapping & qualité | 1 j | Faible |
| 3 | EDA visuelle | 1 j | Moyen (heatmap perf) |
| 4 | **Algo from scratch** | 2 j | **Élevé (cœur TP)** |
| 5 | Reco avancée + explainability | 1.5 j | Moyen |
| 6 | Évaluation & dashboard | 2 j | Élevé (split test, métriques) |
| 7 | UX premium & i18n | 1.5 j | Faible |
| 8 | PDF, tests, déploiement | 1.5 j | Moyen (kaleido sur Cloud) |

**Total estimé** : ≈ 12.5 jours-homme, à étaler selon le calendrier TP.

---

## Règles d'or à ne JAMAIS lâcher

1. La séparation `core/` vs `ui/` — `core/` ne contient aucun import de `streamlit`.
2. La vectorisation NumPy des similarités — aucune double boucle Python sur les items.
3. Le contrat de DataFrame `[user_id, item_id, rating]` issu du Sprint 1 — point de jonction unique.
4. `st.session_state` comme seul état partagé entre les pages — pas de variables globales.
5. La mise en cache via le `file_hash` calculé au Sprint 1 — invalidation propre du cache.
6. Aucune librairie de ML pour le cœur algorithmique — vérifiable par `grep` à tout moment.
7. Aucune persistance disque des données utilisateur — RAM uniquement (RGPD).

---

*— Fin du planning Agile RecoSaaS v1.0 —*
