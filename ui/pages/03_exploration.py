"""Tableau de bord EDA — Plotly + cache Streamlit."""

from __future__ import annotations

import time

import pandas as pd
import plotly.express as px
import streamlit as st

from core.validation import quality_report
from ui import theme
from ui.eda_cached import load_eda_bundle


def _fmt_float(x: float) -> str:
    if pd.isna(x):
        return "—"
    return f"{x:.3g}"


def render() -> None:
    st.title("Exploration des données")

    df = st.session_state.get("clean_df")
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        df = st.session_state.get("raw_df")
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        st.warning(
            "Aucun jeu disponible. Importez des données sur **Accueil & importation**, "
            "puis validez le **mapping** — ou disposez au minimum de `raw_df`."
        )
        return

    required = {"user_id", "item_id", "rating"}
    if not required.issubset(df.columns):
        st.error(f"Colonnes requises manquantes : {sorted(required - set(df.columns))}")
        return

    tpl = theme.plotly_template()

    rep = quality_report(df)
    density = 1.0 - rep["sparsity"]
    st.subheader("Rapport qualité")
    rq1, rq2, rq3, rq4 = st.columns(4)
    with rq1:
        st.metric("Densité", f"{100.0 * density:.2f} %", help="1 − sparsité")
    with rq2:
        st.metric("Doublons (lignes)", f"{rep['n_duplicates']}")
    with rq3:
        st.metric("Cellules manquantes", f"{rep['pct_missing']:.2f} %")
    with rq4:
        st.metric(
            "Plage des notes",
            f"{_fmt_float(rep['rating_min'])} – {_fmt_float(rep['rating_max'])}",
            help=f"Moyenne : {_fmt_float(rep['rating_mean'])}",
        )

    t_page = time.perf_counter()
    bundle = load_eda_bundle(df)
    total_elapsed = time.perf_counter() - t_page
    if total_elapsed > 3.0:
        st.warning(f"Temps de rendu EDA : {total_elapsed:.2f} s (cible : moins de 3 s).")

    kpis = bundle["kpis"]
    st.subheader("Indicateurs clés")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Utilisateurs", f"{kpis['n_users']:,}")
    with m2:
        st.metric("Items", f"{kpis['n_items']:,}")
    with m3:
        st.metric("Interactions", f"{kpis['n_interactions']:,}")
    with m4:
        st.metric("Sparsité", f"{100.0 * kpis['sparsity']:.2f} %")

    st.subheader("Distribution des notes")
    rdf = df.dropna(subset=["rating"])
    if rdf.empty:
        st.info("Aucune note exploitable pour l’histogramme.")
    else:
        fig_hist = px.histogram(
            rdf,
            x="rating",
            nbins=40,
            title="Histogramme des notes",
            labels={"rating": "Note", "count": "Effectif"},
        )
        fig_hist.update_layout(bargap=0.05, template=tpl)
        fig_hist.update_traces(marker_color=theme.PLOTLY_MARKER)
        st.plotly_chart(fig_hist, use_container_width=True)

    top_i = bundle["top_items"]
    top_u = bundle["top_users"]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top 10 items (volume)")
        fig_items = px.bar(
            x=top_i.values,
            y=top_i.index.astype(str),
            orientation="h",
            labels={"x": "Nombre d’interactions", "y": "Item"},
        )
        fig_items.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=420,
            template=tpl,
        )
        fig_items.update_traces(marker_color=theme.PLOTLY_MARKER)
        st.plotly_chart(fig_items, use_container_width=True)

    with c2:
        st.subheader("Top 10 utilisateurs (volume)")
        fig_users = px.bar(
            x=top_u.values,
            y=top_u.index.astype(str),
            orientation="h",
            labels={"x": "Nombre d’interactions", "y": "Utilisateur"},
        )
        fig_users.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=420,
            template=tpl,
        )
        fig_users.update_traces(marker_color=theme.PLOTLY_MARKER_ALT)
        st.plotly_chart(fig_users, use_container_width=True)

    st.subheader("Heatmap (sous-échantillon)")
    heat = bundle["heatmap"]
    if heat.empty:
        st.info("Pas assez de données pour construire une heatmap.")
    else:
        fig_hm = px.imshow(
            heat,
            labels=dict(x="Utilisateur", y="Item", color="Note (moy.)"),
            aspect="auto",
            title="Interactions agrégées (items × utilisateurs)",
            color_continuous_scale=theme.PLOTLY_HEATMAP_SCALE,
        )
        fig_hm.update_layout(template=tpl)
        st.plotly_chart(fig_hm, use_container_width=True)
        if bundle["heatmap_subsampled"]:
            st.caption(
                "**Sous-échantillonnage actif** : seuls les "
                f"**{heat.shape[0]}** items et **{heat.shape[1]}** utilisateurs les plus actifs "
                "sont affichés (top par volume). "
                "La matrice complète serait trop dense pour le navigateur."
            )
        else:
            st.caption(
                "Le jeu comporte au plus 50 utilisateurs et 50 items distincts : "
                "aucun plafond d’effectif n’a été atteint pour le sous-échantillonnage large."
            )


render()
