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

La première page (**Accueil & importation**) présente le projet et l’import des données ; puis mapping → recommandation / dashboard.

## Export des résultats

Sur la page **Recommandation**, après un calcul de top-N, un bouton **Télécharger les recommandations (CSV)** génère un fichier en mémoire (aucune écriture disque côté serveur).

## Tests & qualité (en local)

Pas de pipeline CI imposé pour le TP ; en local :

```bash
python -m ruff check .
pytest
```

## Architecture

La structure suit le planning (`core/`, `ui/`, `tests/`, `data/sample/`) avec **`app.py` à la racine** du dépôt pour `streamlit run app.py`.

- **`core/`** : logique métier pure — **aucun** `import streamlit`.
- **`ui/`** : thème, pages Streamlit.
- **`tests/`** : `pytest` ciblant principalement `core/`.
- **`data/sample/`** : exemple CSV livres (`books_sample.csv`, 100 lignes × 10 colonnes).

Interface en **français** uniquement. Algorithme item–item **from scratch** (`core/similarity.py`, etc.) — voir `requirements.txt` pour l’interdiction de scikit-learn / surprise sur la partie reco.

## Déploiement (bonus note)

Pousser le dépôt sur **GitHub** et connecter le repo à **Streamlit Community Cloud** pour obtenir une **URL publique** ; indiquez ce lien en tête du README ou du rapport de TP.

## Contraintes projet

1. Pas de `scikit-learn` / `surprise` / `implicit` pour le filtrage collaboratif (voir commentaires dans `requirements.txt`).
2. Contrat données : DataFrame **`[user_id, item_id, rating]`** (à partir du Sprint 1).
3. Pas de persistance disque des données utilisateur (RAM / session) — cf. CDC §5.4.

## Licence

MIT — voir [`LICENSE`](LICENSE).
