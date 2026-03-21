# ui/overview.py — Overview tab: visual-first, minimal text

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from services.preprocessing import missing_values_summary, duplicate_count, low_variance_columns
from utils.helpers import get_numeric_columns, get_categorical_columns
from utils.export import figure_to_png_bytes
from config import PALETTE, PREVIEW_ROWS


def _missing_bar_chart(missing: pd.DataFrame) -> plt.Figure:
    """Horizontal bar chart of missing value percentages."""
    fig, ax = plt.subplots(figsize=(7, max(2.5, len(missing) * 0.45)))
    bars = ax.barh(missing.index, missing["Pourcentage (%)"], color=PALETTE["mauve"], height=0.55)
    ax.bar_label(bars, fmt="%.1f%%", padding=4, fontsize=9, color=PALETTE["text"])
    ax.set_xlabel("Pourcentage manquant (%)")
    ax.set_xlim(0, 110)
    ax.invert_yaxis()
    ax.set_facecolor(PALETTE["background"])
    fig.patch.set_facecolor(PALETTE["background"])
    fig.tight_layout()
    return fig


def _dtype_donut(n_num: int, n_cat: int) -> plt.Figure:
    """Donut chart showing numeric vs categorical split."""
    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    sizes = [n_num, n_cat]
    colors = [PALETTE["primary"], PALETTE["secondary"]]
    labels = [f"Numeriques\n{n_num}", f"Categorielles\n{n_cat}"]
    wedges, _ = ax.pie(sizes, colors=colors, startangle=90,
                       wedgeprops={"width": 0.5, "linewidth": 2, "edgecolor": "white"})
    ax.legend(wedges, labels, loc="lower center", ncol=2, frameon=False,
              bbox_to_anchor=(0.5, -0.12), fontsize=9)
    ax.set_title("Repartition des colonnes", fontsize=11, pad=10, color=PALETTE["text"])
    fig.patch.set_facecolor(PALETTE["background"])
    fig.tight_layout()
    return fig


def show_overview(df: pd.DataFrame) -> None:
    num_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)
    missing = missing_values_summary(df)
    n_dup = duplicate_count(df)
    low_var = low_variance_columns(df)

    # ── KPI row ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Lignes", f"{df.shape[0]:,}")
    c2.metric("Colonnes", df.shape[1])
    c3.metric("Numeriques", len(num_cols))
    c4.metric("Categorielles", len(cat_cols))
    c5.metric("Doublons", n_dup, delta=f"-{n_dup}" if n_dup else None,
              delta_color="inverse")

    st.markdown("---")

    # ── Left: column table | Right: donut ────────────────────────────────────
    left, right = st.columns([2, 1])

    with left:
        st.markdown("**Colonnes du dataset**")
        rows = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            kind = "Numerique" if col in num_cols else "Categorielle"
            n_missing = int(df[col].isnull().sum())
            pct = round(n_missing / len(df) * 100, 1)
            rows.append({
                "Colonne": col,
                "Type": dtype,
                "Categorie": kind,
                "Manquants": n_missing,
                "%": f"{pct}%",
            })
        col_df = pd.DataFrame(rows)

        def style_kind(val):
            if val == "Numerique":
                return "background-color:#dde8f7; color:#2a4a80; border-radius:4px; padding:2px 6px;"
            return "background-color:#fde8d8; color:#8a3a0f; border-radius:4px; padding:2px 6px;"

        styled = (
            col_df.style
            .applymap(style_kind, subset=["Categorie"])
            .set_properties(**{"font-size": "13px"})
            .set_table_styles([
                {"selector": "thead th", "props": [
                    ("background-color", "#4C72B0"), ("color", "white"),
                    ("font-weight", "600"), ("padding", "8px 12px"),
                ]},
                {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "#f7f9fc")]},
                {"selector": "tbody td", "props": [("padding", "6px 12px")]},
            ])
            .hide(axis="index")
        )
        st.dataframe(styled, use_container_width=True, height=min(400, 45 + len(col_df) * 38))

    with right:
        fig_donut = _dtype_donut(len(num_cols), len(cat_cols))
        st.pyplot(fig_donut, use_container_width=True)
        plt.close(fig_donut)

    st.markdown("---")

    # ── Missing values ────────────────────────────────────────────────────────
    st.markdown("**Valeurs manquantes**")
    if missing.empty:
        st.success("Aucune valeur manquante dans ce dataset.")
    else:
        fig_miss = _missing_bar_chart(missing)
        col_fig, col_table = st.columns([2, 1])
        with col_fig:
            st.pyplot(fig_miss, use_container_width=True)
            st.download_button(
                "Telecharger PNG", figure_to_png_bytes(fig_miss),
                "missing_values.png", "image/png",
            )
        with col_table:
            st.dataframe(missing, use_container_width=True)
        plt.close(fig_miss)

    st.markdown("---")

    # ── Low variance alert ────────────────────────────────────────────────────
    st.markdown("**Variance des colonnes**")
    if not low_var:
        st.success("Aucune colonne quasi-constante detectee.")
    else:
        st.warning(
            f"{len(low_var)} colonne(s) a faible variance : "
            + "  ·  ".join(f"`{c}`" for c in low_var)
            + "  — candidates a la suppression."
        )

    st.markdown("---")

    # ── Data preview ─────────────────────────────────────────────────────────
    with st.expander("Apercu des donnees brutes", expanded=False):
        st.dataframe(df.head(PREVIEW_ROWS), use_container_width=True)
