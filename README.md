# Ijora

Plateforme **SaaS de recommandation intelligente** (filtrage collaboratif **item–item**, implémentation **from scratch** avec `pandas` / `numpy` uniquement pour la partie ML).  
Projet dans le cadre d’un **TP Big Data / Machine Learning** (RecoSaaS, CDC v2).

## Dépôt distant

- GitHub : [https://github.com/Guck2005/ijora.git](https://github.com/Guck2005/ijora.git)

Après le premier commit local :

```bash
git remote add origin https://github.com/Guck2005/ijora.git
git push -u origin main
```

## Prérequis

- Python **3.10+**
- Un environnement virtuel recommandé

## Installation

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Lancer l’application

```bash
streamlit run app.py
```

La page d’accueil affiche **Hello RecoSaaS** (squelette Sprint 0).

## Tests & qualité

```bash
python -m ruff check .
pytest
```

## Architecture (Sprint 0)

La structure suit le planning (`core/`, `ui/`, `tests/`, `data/sample/`) avec **`app.py` à la racine** du dépôt pour satisfaire la commande `streamlit run app.py` (équivalent fonctionnel du dossier `recosaas/` décrit dans `Sprints_Planning.md`).

- **`core/`** : logique métier pure — **aucun** `import streamlit`.
- **`ui/`** : thème, i18n, pages et composants Streamlit.
- **`tests/`** : `pytest` ciblant principalement `core/`.
- **`data/sample/`** : échantillons (ex. extrait type MovieLens pour les sprints suivants).

Les détails des sprints sont dans [`Sprints_Planning.md`](Sprints_Planning.md) (Sprint 0 → initialisation ; Sprint 1+ ingestion, mapping, EDA, similarité, etc.).

## Contraintes projet

1. Pas de `scikit-learn` / `surprise` / `implicit` pour le filtrage collaboratif (voir commentaires dans `requirements.txt`).
2. Contrat données : DataFrame **`[user_id, item_id, rating]`** (à partir du Sprint 1).
3. Pas de persistance disque des données utilisateur (RAM / session) — cf. CDC §5.4.

## Licence

MIT — voir [`LICENSE`](LICENSE).
