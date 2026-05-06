"""Accueil + importation — présentation du projet et modes CSV / saisie manuelle."""

from __future__ import annotations

import hashlib
import time
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from core.eda import compute_dataset_signature
from core.ingestion import STANDARD_COLUMNS, build_manual_dataframe, load_csv, standardize
from core.mapping import suggest_mapping
from core.validation import validate_file_size, validate_rating_column

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SAMPLE_BOOKS = _PROJECT_ROOT / "data" / "sample" / "books_sample.csv"
_RECO_PAGE = Path(__file__).resolve().parent / "04_recommandation.py"

# Hauteur du viewport du tableau (px) : défilement vertical pour voir toutes les lignes.
_SCROLLABLE_TABLE_HEIGHT = 420


def _ensure_session_defaults() -> None:
    defaults: dict[str, object] = {
        "file_hash": None,
        "raw_df": None,
        "manual_editor_df": None,
        "csv_demo_buffer": None,
        "import_staging_df": None,
        "clean_df": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    if st.session_state.get("ingestion_mode") not in ("csv", "manual"):
        st.session_state["ingestion_mode"] = "csv"


def _work_dataframe() -> pd.DataFrame | None:
    staging = st.session_state.get("import_staging_df")
    if isinstance(staging, pd.DataFrame) and not staging.empty:
        return staging
    raw = st.session_state.get("raw_df")
    if raw is None or not isinstance(raw, pd.DataFrame) or raw.empty:
        return None
    return raw


def _cold_start_rows() -> list[dict]:
    return [
        {"user_id": 1, "item_id": 10, "rating": 5.0},
        {"user_id": 1, "item_id": 22, "rating": 3.0},
        {"user_id": 1, "item_id": 34, "rating": 4.0},
        {"user_id": 2, "item_id": 10, "rating": 4.0},
        {"user_id": 2, "item_id": 15, "rating": 2.0},
        {"user_id": 3, "item_id": 10, "rating": 1.0},
        {"user_id": 3, "item_id": 22, "rating": 5.0},
        {"user_id": 4, "item_id": 7, "rating": 3.0},
        {"user_id": 5, "item_id": 99, "rating": 4.0},
        {"user_id": 5, "item_id": 12, "rating": 2.0},
    ]


def _empty_editor_df() -> pd.DataFrame:
    return pd.DataFrame(
        [{c: pd.NA for c in STANDARD_COLUMNS} for _ in range(3)],
        columns=list(STANDARD_COLUMNS),
    )


def _editor_column_config() -> dict:
    return {
        "user_id": st.column_config.TextColumn(
            "Utilisateur",
            help="Identifiant utilisateur",
            max_chars=64,
        ),
        "item_id": st.column_config.TextColumn(
            "Item",
            help="Identifiant item / livre",
            max_chars=64,
        ),
        "rating": st.column_config.NumberColumn(
            "Note",
            min_value=0.0,
            max_value=5.0,
            step=0.5,
            format="%.1f",
        ),
    }


def _render_mapping_section() -> None:
    work_df = _work_dataframe()
    if work_df is None:
        return

    columns = list(work_df.columns)
    if len(columns) < 3:
        st.error("Moins de 3 colonnes : impossible de mapper correctement.")
        return

    sug = suggest_mapping(columns)

    def _default_index(col_name: str | None, fallback: int) -> int:
        if col_name in columns:
            return columns.index(col_name)
        return min(fallback, len(columns) - 1)

    st.subheader("Mapping des colonnes")
    st.caption(
        "Suggestion automatique (modifiable) — les trois colonnes doivent être distinctes."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        u_sel = st.selectbox(
            "Colonne User_ID",
            columns,
            index=_default_index(sug.get("user_id"), 0),
            key="map_col_user",
        )
    with c2:
        i_sel = st.selectbox(
            "Colonne Item_ID",
            columns,
            index=_default_index(sug.get("item_id"), min(1, len(columns) - 1)),
            key="map_col_item",
        )
    with c3:
        r_sel = st.selectbox(
            "Colonne Rating",
            columns,
            index=_default_index(sug.get("rating"), min(2, len(columns) - 1)),
            key="map_col_rating",
        )

    if len({u_sel, i_sel, r_sel}) < 3:
        st.error(
            "Colonnes mal mappées : les trois champs doivent désigner des colonnes **distinctes**."
        )
        return

    try:
        mapped = standardize(work_df, u_sel, i_sel, r_sel)
    except KeyError as e:
        st.error(f"Colonnes mal mappées ou absentes : {e}")
        return

    vr = validate_rating_column(mapped["rating"])

    if not vr["ok"]:
        st.error(
            f"**Notes non numériques** — {vr['n_invalid']} valeur(s) invalide(s) "
            f"(dtype colonne : `{vr['dtype']}`)."
        )
        bad_idx = vr["invalid_indices"][:10]
        if bad_idx:
            st.dataframe(mapped.iloc[bad_idx], use_container_width=True)

    ratings_ok = bool(vr["ok"])

    if st.button(
        "Valider le mapping et enregistrer clean_df",
        type="primary",
        disabled=not ratings_ok,
        key="btn_save_clean_df",
    ):
        out = mapped.copy()
        st.session_state["raw_df"] = mapped.reset_index(drop=True)
        st.session_state["clean_df"] = out.reset_index(drop=True)
        st.session_state["dataset_sig"] = compute_dataset_signature(st.session_state["clean_df"])
        # Consommée après standardisation — évite de re-parser un jeu déjà canonique.
        st.session_state["import_staging_df"] = None
        st.switch_page(_RECO_PAGE)


def render() -> None:
    _ensure_session_defaults()

    st.title("RecoSaaS — Ijora")
    st.markdown(
        "Plateforme de recommandation par **filtrage collaboratif item–item**."
    )
    st.markdown(
        """
        <div class="ijora-import-steps">
            <div class="ijora-import-step">
                1. <strong>Importation</strong> (ci-dessous) — CSV ou saisie manuelle.
            </div>
            <div class="ijora-import-step">
                2. <strong>Mapping des colonnes</strong> sur cette page après import.
            </div>
            <div class="ijora-import-step">
                3. <strong>Recommandation</strong> — ouverte automatiquement après validation du
                mapping.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("Importation des données")

    mode = st.radio(
        "Mode d'ingestion",
        ["csv", "manual"],
        horizontal=True,
        format_func=lambda m: "Fichier CSV" if m == "csv" else "Saisie manuelle",
        key="ingestion_mode",
    )

    st.divider()

    if mode == "csv":
        _render_csv_mode()
    else:
        _render_manual_mode()

    st.divider()
    _render_mapping_section()

    st.divider()
    raw = st.session_state.get("raw_df")
    if raw is not None and isinstance(raw, pd.DataFrame) and not raw.empty:
        st.success(
            f"**Jeu chargé en session** — {len(raw)} lignes, colonnes : {list(raw.columns)}."
        )
        st.dataframe(
            raw,
            use_container_width=True,
            height=_SCROLLABLE_TABLE_HEIGHT,
        )
    elif raw is not None and isinstance(raw, pd.DataFrame) and raw.empty:
        st.warning("Le DataFrame en session est vide : complétez ou rechargez des données.")


def _render_csv_mode() -> None:
    st.subheader("Mode fichier CSV")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        uploaded = st.file_uploader(
            "Glissez-déposez un fichier CSV / TSV (ou choisissez un fichier)",
            type=["csv", "txt", "dat", "tsv"],
            help="Lecture en RAM uniquement (BytesIO).",
        )
    with col_b:
        st.caption("Exemple local (fichier du dépôt, lecture → RAM)")
        if st.button("Charger l'exemple livres (100 lignes)", use_container_width=True):
            if _SAMPLE_BOOKS.is_file():
                st.session_state["csv_demo_buffer"] = _SAMPLE_BOOKS.read_bytes()
            else:
                st.error(
                    "books_sample.csv introuvable — lancer scripts/generate_books_sample.py"
                )

    if uploaded is not None:
        st.session_state["csv_demo_buffer"] = None

    buf = st.session_state.get("csv_demo_buffer")
    file_obj = uploaded if uploaded is not None else (BytesIO(buf) if buf else None)

    if file_obj is None:
        return

    check = validate_file_size(file_obj)
    for w in check["warnings"]:
        st.warning(w)
    if not check["ok"]:
        st.error(check["warnings"][0] if check["warnings"] else "Fichier refusé.")
        return

    if hasattr(file_obj, "getvalue"):
        st.session_state["file_hash"] = hashlib.md5(file_obj.getvalue()).hexdigest()

    t0 = time.perf_counter()
    try:
        loaded = load_csv(file_obj)
    except Exception as e:  # noqa: BLE001 — UI : message lisible
        st.error(f"Lecture impossible : {e}")
        return
    elapsed = time.perf_counter() - t0
    if elapsed > 2.0:
        st.warning(f"Chargement un peu long ({elapsed:.2f} s) — envisagez un extrait plus petit.")

    cols = list(loaded.columns)

    st.dataframe(
        loaded,
        use_container_width=True,
        height=_SCROLLABLE_TABLE_HEIGHT,
    )

    if len(cols) < 3:
        st.error("Le fichier doit contenir au moins 3 colonnes (utilisateur, item, note).")
        return

    if st.button(
        "Importer le fichier en session (mapping ci-dessous)",
        type="primary",
        key="csv_validate",
    ):
        st.session_state["import_staging_df"] = loaded.copy()
        st.session_state["raw_df"] = None
        st.session_state["clean_df"] = None
        st.session_state.pop("dataset_sig", None)


def _render_manual_mode() -> None:
    st.subheader("Mode saisie manuelle")

    if st.button("Charger un exemple cold-start (10 lignes)", key="btn_cold_start"):
        st.session_state["manual_editor_df"] = pd.DataFrame(_cold_start_rows())

    if st.session_state["manual_editor_df"] is None:
        st.session_state["manual_editor_df"] = _empty_editor_df()

    edited = st.data_editor(
        st.session_state["manual_editor_df"],
        num_rows="dynamic",
        column_config=_editor_column_config(),
        use_container_width=True,
        height=_SCROLLABLE_TABLE_HEIGHT,
        key="manual_data_editor_widget",
    )
    st.session_state["manual_editor_df"] = edited

    if st.button(
        "Valider la saisie et charger pour le mapping",
        type="primary",
        key="manual_validate",
    ):
        rows = edited.to_dict(orient="records")
        built = build_manual_dataframe(rows)
        if built.empty:
            st.error("Aucune ligne valide : remplissez au moins une ligne complète.")
            return
        st.session_state["import_staging_df"] = built.copy()
        st.session_state["raw_df"] = None
        st.session_state["clean_df"] = None
        st.session_state.pop("dataset_sig", None)
        st.session_state["file_hash"] = None


render()
