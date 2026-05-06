"""Page recommandation — similarité item–item, top-N et tableau de bord."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.matrix import build_item_index_map, build_pivot_matrix
from core.metrics import rating_bin_profile
from core.recommender import compute_item_popularity, recommend_top_n
from ui import theme
from ui.reco_cache import cached_similarity_matrix


def _render_reco_dashboard(df: pd.DataFrame) -> None:
    """Graphiques (barres, heatmap, radar) — même logique que l’ancien Dashboard."""
    tpl = theme.plotly_template()

    res = st.session_state.get("reco_last_results")
    sim = st.session_state.get("sim_matrix")
    idx_map: dict[str, int] = st.session_state.get("sim_item_index") or {}
    target_raw = st.session_state.get("reco_last_target")

    if (
        isinstance(res, pd.DataFrame)
        and not res.empty
        and sim is not None
        and idx_map
        and target_raw
    ):
        tid = str(target_raw).split(",")[0].strip()

        fig_bar = px.bar(
            res,
            x="similarity_score",
            y="item_id",
            orientation="h",
            labels={"similarity_score": "Similarité", "item_id": "Item"},
            title="Scores des items recommandés",
        )
        fig_bar.update_layout(template=tpl, yaxis={"categoryorder": "total ascending"})
        fig_bar.update_traces(marker_color=theme.PLOTLY_MARKER)
        st.plotly_chart(fig_bar, use_container_width=True)

        rec_ids = [str(x) for x in res["item_id"].tolist()]
        if tid in idx_map:
            rec_f = [r for r in rec_ids if r in idx_map and r != tid]
            idxs = [idx_map[tid]] + [idx_map[r] for r in rec_f]
            labs = [tid] + rec_f
            if len(idxs) >= 2:
                sub = sim[np.ix_(idxs, idxs)]
                fig_hm = px.imshow(
                    sub,
                    x=labs,
                    y=labs,
                    labels=dict(x="Item", y="Item", color="Similarité"),
                    title="Similarité : cible × recommandations",
                    color_continuous_scale=theme.PLOTLY_HEATMAP_SCALE,
                )
                fig_hm.update_layout(template=tpl)
                st.plotly_chart(fig_hm, use_container_width=True)
        else:
            st.caption("Heatmap indisponible (cible absente de la matrice).")

        rec_for_prof = [r for r in rec_ids if r in set(df["item_id"].astype(str))][:10]
        p_tgt = rating_bin_profile(df.loc[df["item_id"].astype(str) == tid, "rating"])
        if rec_for_prof:
            profs = [
                rating_bin_profile(df.loc[df["item_id"].astype(str) == rid, "rating"])
                for rid in rec_for_prof
            ]
            p_mean = np.mean(np.stack(profs, axis=0), axis=0)
        else:
            p_mean = np.zeros(5)

        theta = ["1-2", "2-3", "3-4", "4-5", "5"]
        fig_r = go.Figure()
        r_close = np.append(p_tgt, p_tgt[0])
        t_close = theta + [theta[0]]
        fig_r.add_trace(
            go.Scatterpolar(
                r=r_close,
                theta=t_close,
                fill="toself",
                name="Item cible",
                line=dict(color=theme.PLOTLY_MARKER, width=2),
                fillcolor="rgba(22, 101, 52, 0.25)",
            ),
        )
        r2_close = np.append(p_mean, p_mean[0])
        fig_r.add_trace(
            go.Scatterpolar(
                r=r2_close,
                theta=t_close,
                fill="toself",
                name="Moy. recommandés",
                line=dict(color=theme.PLOTLY_MARKER_ALT, width=2),
                fillcolor="rgba(34, 197, 94, 0.2)",
            ),
        )
        fig_r.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title="Profil des notes (parts par tranche)",
            template=tpl,
        )
        st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.info(
            "Obtenez d’abord une liste de recommandations ci-dessus pour afficher les graphiques."
        )


def render() -> None:
    st.title("Recommandation (similarité item–item)")

    if st.session_state.get("reco_metric_select") not in ("cosine", "pearson"):
        st.session_state["reco_metric_select"] = "cosine"

    df = st.session_state.get("clean_df")
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        df = st.session_state.get("raw_df")
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        st.warning(
            "Chargez un jeu sur **Accueil & importation**, puis **validez le mapping** "
            "pour produire `clean_df`."
        )
        return

    required = {"user_id", "item_id", "rating"}
    if not required.issubset(df.columns):
        st.error("Jeu incompatible : colonnes user_id, item_id, rating requises.")
        return

    pivot = build_pivot_matrix(df)
    if pivot.shape[0] < 2:
        st.error("Au moins deux items sont nécessaires pour une matrice de similarité.")
        return

    labels = pd.Index(pivot.index.astype(str))
    n_max = max(1, min(20, pivot.shape[0] - 1))

    metric_key = st.session_state.get("reco_metric_select", "cosine")
    if metric_key not in ("cosine", "pearson"):
        metric_key = "cosine"

    st.subheader("Filtres pour les listes de recommandations")
    threshold = st.slider(
        "Seuil de similarité minimum",
        0.0,
        1.0,
        0.0,
        step=0.05,
        key="reco_threshold_slider",
        help="Ignore les voisins dont la similarité est strictement inférieure à ce seuil.",
    )
    min_pop = st.number_input(
        "Popularité minimale (nombre d’interactions)",
        min_value=0,
        value=1,
        step=1,
        help="Items ayant moins de notes que ce seuil sont exclus.",
        key="reco_min_pop",
    )

    st.divider()
    st.subheader("Paramètres de recommandation")

    n_rec = st.slider(
        "Nombre de recommandations (N)",
        1,
        n_max,
        min(5, n_max),
        key="reco_n_slider",
        help="Nombre d’items à retourner (hors item cible).",
    )

    target_id = st.selectbox(
        "Choisir un item (recherche intégrée)",
        options=list(labels),
        key="reco_target_selectbox",
    )

    if st.button("Obtenir les recommandations", type="primary", key="reco_btn_topn"):
        if target_id is None or (isinstance(target_id, str) and not str(target_id).strip()):
            st.warning("Choisissez un item cible.")
            return
        tid = str(target_id).strip()

        fh = st.session_state.get("file_hash")
        sig = st.session_state.get("dataset_sig")
        sim_df = cached_similarity_matrix(fh, sig, metric_key, pivot)

        sim = sim_df.to_numpy(dtype="float64", copy=False)
        idx_map = build_item_index_map(pivot)
        st.session_state["sim_matrix"] = sim
        st.session_state["sim_item_index"] = idx_map
        st.session_state["reco_pivot_index"] = labels
        st.session_state["sim_metric"] = metric_key
        st.session_state["sim_pivot_shape"] = pivot.shape

        pop_counts = compute_item_popularity(df)
        pop_aligned = pop_counts.reindex(labels).fillna(0).astype(int)

        if tid not in idx_map:
            st.warning(
                "Item cible **sans ligne dans la matrice** (aucune interaction exploitable "
                "pour la similarité). Essayez un autre ID ou importez plus de données."
            )
            alts = pop_counts.nlargest(10)
            st.dataframe(
                alts.rename("popularité").to_frame(),
                use_container_width=True,
            )
            return

        item_idx = int(idx_map[tid])
        res = recommend_top_n(
            sim,
            item_idx,
            n_rec,
            float(threshold),
            int(min_pop),
            pop_aligned,
        )
        st.session_state["reco_last_results"] = res
        st.session_state["reco_last_target"] = tid

        if res.empty:
            st.info(
                "Aucun item ne satisfait les filtres (seuil / popularité). "
                "Assouplissez les critères ou augmentez N (dans la limite du catalogue)."
            )
        else:
            st.dataframe(res, use_container_width=True, hide_index=True)

    st.divider()
    with st.expander("Tableau de bord — restitution visuelle", expanded=False):
        _render_reco_dashboard(df)


render()
