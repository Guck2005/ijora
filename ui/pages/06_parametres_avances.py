"""Métrique de similarité (Pearson / Cosinus)."""

from __future__ import annotations

import streamlit as st

_SESSION_SIM_KEYS = (
    "sim_matrix",
    "sim_item_index",
    "reco_pivot_index",
    "sim_metric",
    "sim_pivot_shape",
    "reco_last_results",
    "reco_last_target",
)


def _ensure_metric_default() -> None:
    if st.session_state.get("reco_metric_select") not in ("cosine", "pearson"):
        st.session_state["reco_metric_select"] = "cosine"


def _invalidate_similarity_session() -> None:
    for k in _SESSION_SIM_KEYS:
        st.session_state.pop(k, None)


def render() -> None:
    _ensure_metric_default()

    st.title("Métrique de similarité")

    metric_key = st.selectbox(
        "Métrique",
        ["cosine", "pearson"],
        format_func=lambda k: "Cosinus" if k == "cosine" else "Pearson",
        key="reco_metric_select",
        help=(
            "Pearson : vecteurs centrés (corrèle les écarts à la moyenne). "
            "Cosinus : vecteurs bruts (absences souvent traitées comme 0)."
        ),
    )

    prev_choice = st.session_state.get("_last_metric_choice_ui")
    if prev_choice is not None and prev_choice != metric_key:
        _invalidate_similarity_session()
        st.info(
            "Métrique modifiée : la matrice et la dernière liste de recommandations ont été "
            "réinitialisées. Recalculez avec **Obtenir les recommandations** sur la page dédiée."
        )
    st.session_state["_last_metric_choice_ui"] = metric_key

    with st.expander("Comprendre la différence Cosinus / Pearson"):
        st.markdown(
            """
**Pearson (corrélation centrée)**  
Pour chaque item, on retire la **moyenne des notes** de cet item sur les utilisateurs
qui l’ont noté. On compare ensuite les **écarts** (« plus haut / plus bas que la moyenne »).
Utile quand les utilisateurs ne notent pas sur la même échelle : ce qui compte, c’est le
**profil relatif**, pas l’intensité absolue.

**Cosinus**  
On compare les vecteurs de notes **tels quels** (souvent avec des 0 là où il n’y a pas de note).
Deux items sont « proches » si les **patterns de présence / intensité** des notes se ressemblent.

**En résumé**  
- Pearson → insiste sur les **tendances relatives**
  (corrélé / anti-corrélé au comportement moyen).  
- Cosinus → insiste sur la **direction** du vecteur dans l’espace des utilisateurs.

La matrice est calculée lorsque vous cliquez sur **Obtenir les recommandations** sur la page
**Recommandation** (avec la métrique choisie ici).
            """
        )

    st.divider()
    st.subheader("État de la session")

    sim = st.session_state.get("sim_matrix")
    shape = st.session_state.get("sim_pivot_shape")
    active = st.session_state.get("sim_metric")

    if sim is not None and shape is not None:
        if active == "pearson":
            ml = "Pearson"
        elif active == "cosine":
            ml = "Cosinus"
        else:
            ml = str(active)
        st.success(
            f"Dernier calcul : **{active}** ({ml}) — pivot : "
            f"**{shape[0]} × {shape[1]}** (items × utilisateurs)."
        )
    else:
        st.info(
            "Aucune matrice encore calculée dans cette session. Sur **Recommandation**, "
            f"cliquez sur **Obtenir les recommandations** (métrique actuelle : **{metric_key}**)."
        )


render()
