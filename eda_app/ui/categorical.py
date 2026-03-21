# ui/categorical.py — Categorical analysis tab, visual-first

import streamlit as st
import pandas as pd

from services.analysis import value_counts_table, contingency_table
from visuals.plots import plot_bar, plot_pie, plot_boxplot_by_cat, plot_violin_by_cat
from utils.helpers import get_categorical_columns, get_numeric_columns
from utils.export import figure_to_png_bytes
from config import PIE_MAX_CATEGORIES
import matplotlib.pyplot as plt


def _styled_vc(vc: pd.DataFrame) -> None:
    styled = (
        vc.style
        .background_gradient(subset=["Effectif"], cmap="Blues")
        .format({"Pourcentage (%)": "{:.1f}%"})
        .set_table_styles([
            {"selector": "thead th", "props": [
                ("background-color", "#4C72B0"), ("color", "white"),
                ("font-weight", "600"), ("padding", "8px 12px"),
            ]},
            {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "#f7f9fc")]},
            {"selector": "tbody td", "props": [("padding", "6px 12px")]},
        ])
    )
    st.dataframe(styled, use_container_width=True, height=min(380, 50 + len(vc) * 38))


def analyze_categorical(df: pd.DataFrame) -> None:
    cat_cols = get_categorical_columns(df)
    num_cols = get_numeric_columns(df)

    if not cat_cols:
        st.info("Aucune colonne categorielle disponible.")
        return

    # ── Column selector ───────────────────────────────────────────────────────
    col = st.selectbox("Colonne categorielle", options=cat_cols)
    n_cats = df[col].nunique(dropna=False)

    st.markdown("---")

    # ── Distribution: chart left, table right ─────────────────────────────────
    st.markdown("**Distribution**")
    c1, c2 = st.columns([2, 1])

    with c1:
        if n_cats <= PIE_MAX_CATEGORIES:
            fig = plot_pie(df, col)
            label = "pie"
        else:
            fig = plot_bar(df, col)
            label = "bar"
        st.pyplot(fig, use_container_width=True)
        st.download_button("PNG", figure_to_png_bytes(fig),
                           f"{label}_{col}.png", "image/png")
        plt.close(fig)

    with c2:
        vc = value_counts_table(df, col)
        _styled_vc(vc)

    st.markdown("---")

    # ── Cross analysis with numeric ───────────────────────────────────────────
    if num_cols:
        st.markdown("**Analyse croisee — variable numerique**")
        num_col = st.selectbox("Variable numerique", options=num_cols)

        cx1, cx2 = st.columns(2)
        with cx1:
            st.markdown(f"Boxplot · `{num_col}` par `{col}`")
            fig = plot_boxplot_by_cat(df, num_col, col)
            st.pyplot(fig, use_container_width=True)
            st.download_button("PNG", figure_to_png_bytes(fig),
                               f"box_{num_col}_{col}.png", "image/png", key="dl_box")
            plt.close(fig)

        with cx2:
            st.markdown(f"Violin · `{num_col}` par `{col}`")
            fig = plot_violin_by_cat(df, num_col, col)
            st.pyplot(fig, use_container_width=True)
            st.download_button("PNG", figure_to_png_bytes(fig),
                               f"vio_{num_col}_{col}.png", "image/png", key="dl_vio")
            plt.close(fig)

        st.markdown("---")

    # ── Contingency table ─────────────────────────────────────────────────────
    other_cat = [c for c in cat_cols if c != col]
    if other_cat:
        st.markdown("**Table de contingence**")
        col_b = st.selectbox("Deuxieme variable", options=other_cat)
        ct = contingency_table(df, col, col_b)
        styled_ct = (
            ct.style
            .background_gradient(cmap="Blues")
            .set_table_styles([
                {"selector": "thead th", "props": [
                    ("background-color", "#4C72B0"), ("color", "white"),
                    ("font-weight", "600"), ("padding", "8px 12px"),
                ]},
                {"selector": "tbody td", "props": [("padding", "6px 12px")]},
            ])
        )
        st.dataframe(styled_ct, use_container_width=True)
