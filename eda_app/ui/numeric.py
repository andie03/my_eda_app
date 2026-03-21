# ui/numeric.py — Numeric analysis tab, visual-first

import streamlit as st
import pandas as pd

from services.analysis import descriptive_stats, detect_outliers_iqr, correlation_matrix, strong_correlations
from visuals.plots import plot_histogram, plot_boxplot, plot_scatter, plot_corr_matrix
from utils.helpers import get_numeric_columns
from utils.export import figure_to_png_bytes
from config import STRONG_CORR_THRESHOLD
import matplotlib.pyplot as plt


def _stats_cards(stats: pd.DataFrame) -> None:
    """Display stats as a styled dataframe with color-coded skewness."""
    def color_skew(val):
        try:
            v = float(val)
            if abs(v) > 1:
                return "background-color:#fde8d8; color:#8a3a0f;"
            elif abs(v) > 0.5:
                return "background-color:#fff8e1; color:#6b4c00;"
            return "background-color:#e8f5e9; color:#1b5e20;"
        except Exception:
            return ""

    styled = (
        stats.style
        .applymap(color_skew, subset=["Skewness"])
        .format("{:.3f}")
        .set_table_styles([
            {"selector": "thead th", "props": [
                ("background-color", "#4C72B0"), ("color", "white"),
                ("font-weight", "600"), ("padding", "8px 12px"),
            ]},
            {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "#f7f9fc")]},
            {"selector": "tbody td", "props": [("padding", "6px 12px")]},
        ])
    )
    st.dataframe(styled, use_container_width=True)


def analyze_numeric(df: pd.DataFrame) -> None:
    num_cols = get_numeric_columns(df)

    if not num_cols:
        st.info("Aucune colonne numerique disponible.")
        return

    # ── Column selector ───────────────────────────────────────────────────────
    selected = st.multiselect(
        "Colonnes a analyser",
        options=num_cols,
        default=num_cols[:min(3, len(num_cols))],
    )
    if not selected:
        st.warning("Selectionnez au moins une colonne.")
        return

    # ── Stats table ───────────────────────────────────────────────────────────
    stats = descriptive_stats(df, selected)
    _stats_cards(stats)

    st.markdown("---")

    # ── Per-column visuals ────────────────────────────────────────────────────
    for col in selected:
        st.markdown(f"**{col}**")
        c1, c2, c3 = st.columns(3)

        with c1:
            fig = plot_histogram(df, col)
            st.pyplot(fig, use_container_width=True)
            st.download_button("PNG", figure_to_png_bytes(fig),
                               f"hist_{col}.png", "image/png", key=f"h_{col}")
            plt.close(fig)

        with c2:
            fig = plot_boxplot(df, col)
            st.pyplot(fig, use_container_width=True)
            st.download_button("PNG", figure_to_png_bytes(fig),
                               f"box_{col}.png", "image/png", key=f"b_{col}")
            plt.close(fig)

        with c3:
            outliers = detect_outliers_iqr(df, col)
            n_out = len(outliers)
            total = df[col].dropna().shape[0]
            pct = round(n_out / total * 100, 1) if total else 0
            st.metric("Outliers (IQR)", n_out, delta=f"{pct}%",
                      delta_color="inverse" if n_out else "off")
            if n_out:
                with st.expander("Valeurs extremes"):
                    st.dataframe(outliers.head(20), use_container_width=True)
            else:
                st.success("Aucun outlier detecte.")

        st.markdown("---")

    # ── Scatter ───────────────────────────────────────────────────────────────
    if len(selected) >= 2:
        st.markdown("**Nuage de points**")
        sc1, sc2 = st.columns(2)
        with sc1:
            x_col = st.selectbox("Variable X", options=selected, key="sx")
        with sc2:
            y_opts = [c for c in selected if c != x_col]
            y_col = st.selectbox("Variable Y", options=y_opts, key="sy")
        if x_col and y_col:
            fig = plot_scatter(df, x_col, y_col)
            st.pyplot(fig, use_container_width=True)
            st.download_button("PNG", figure_to_png_bytes(fig),
                               f"scatter_{x_col}_{y_col}.png", "image/png")
            plt.close(fig)
        st.markdown("---")

    # ── Correlation matrix ────────────────────────────────────────────────────
    st.markdown("**Matrice de correlation**")
    if len(num_cols) < 2:
        st.info("Pas assez de colonnes numeriques.")
        return

    corr = correlation_matrix(df)
    fig_corr = plot_corr_matrix(corr)
    st.pyplot(fig_corr, use_container_width=True)
    st.download_button("PNG", figure_to_png_bytes(fig_corr),
                       "correlation_matrix.png", "image/png")
    plt.close(fig_corr)

    # Strong correlations
    strong = strong_correlations(corr, STRONG_CORR_THRESHOLD)
    if not strong.empty:
        st.markdown(f"**Correlations fortes** (|r| ≥ {STRONG_CORR_THRESHOLD})")

        def color_corr(val):
            try:
                v = float(val)
                if v >= 0.9: return "background-color:#c8e6c9; color:#1b5e20;"
                if v >= 0.7: return "background-color:#fff9c4; color:#5c4300;"
                if v <= -0.7: return "background-color:#ffccbc; color:#6d2a00;"
            except Exception:
                pass
            return ""

        styled = (
            strong.style
            .applymap(color_corr, subset=["Correlation"])
            .format({"Correlation": "{:.3f}"})
            .set_table_styles([
                {"selector": "thead th", "props": [
                    ("background-color", "#4C72B0"), ("color", "white"),
                    ("font-weight", "600"), ("padding", "8px 12px"),
                ]},
                {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "#f7f9fc")]},
            ])
            .hide(axis="index")
        )
        st.dataframe(styled, use_container_width=True)
