# visuals/plots.py — Pure plotting functions (data → matplotlib figure)

import hashlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from config import PALETTE, PASTEL_CYCLE, MULTI_PALETTE

# ── Global theme ──────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette=MULTI_PALETTE)
plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   13,
    "axes.labelsize":   11,
    "axes.facecolor":   PALETTE["background"],
    "figure.facecolor": PALETTE["background"],
    "text.color":       PALETTE["text"],
    "axes.labelcolor":  PALETTE["text"],
    "xtick.color":      PALETTE["text"],
    "ytick.color":      PALETTE["text"],
})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _col_color(column: str) -> str:
    """Deterministic pastel color tied to a column name via MD5."""
    idx = int(hashlib.md5(column.encode()).hexdigest(), 16) % len(PASTEL_CYCLE)
    return PASTEL_CYCLE[idx]


def _col_color_pair(column: str):
    """Return (fill, kde_line) — harmonious pair for a column."""
    idx = int(hashlib.md5(column.encode()).hexdigest(), 16) % len(PASTEL_CYCLE)
    kde_idx = (idx + 4) % len(PASTEL_CYCLE)
    return PASTEL_CYCLE[idx], PASTEL_CYCLE[kde_idx]


def _cycle_n(n: int) -> list:
    return [PASTEL_CYCLE[i % len(PASTEL_CYCLE)] for i in range(n)]


# ── Histogramme — GRAND ───────────────────────────────────────────────────────

def plot_histogram(df: pd.DataFrame, column: str) -> plt.Figure:
    fill, kde_col = _col_color_pair(column)
    fig, ax = plt.subplots(figsize=(13, 7))          # GRAND
    fig.patch.set_facecolor(PALETTE["background"])
    sns.histplot(df[column].dropna(), kde=True, ax=ax,
                 color=fill, edgecolor="white", alpha=0.80, linewidth=0.6)
    if ax.lines:
        ax.lines[0].set_color(kde_col)
        ax.lines[0].set_linewidth(2.5)
    ax.set_title(f"Distribution — {column}", fontsize=14, pad=12)
    ax.set_xlabel(column, fontsize=12)
    ax.set_ylabel("Frequence", fontsize=12)
    ax.tick_params(labelsize=11)
    fig.tight_layout()
    return fig


# ── Boxplot individuel — GRAND ────────────────────────────────────────────────

def plot_boxplot(df: pd.DataFrame, column: str) -> plt.Figure:
    color = _col_color(column)
    flier_color = PASTEL_CYCLE[(PASTEL_CYCLE.index(color) + 5) % len(PASTEL_CYCLE)]
    fig, ax = plt.subplots(figsize=(10, 8))          # GRAND
    fig.patch.set_facecolor(PALETTE["background"])
    sns.boxplot(
        y=df[column].dropna(), ax=ax, color=color, linewidth=2.0,
        flierprops={"marker": "o", "markerfacecolor": flier_color,
                    "markersize": 6, "alpha": 0.75, "markeredgewidth": 0},
    )
    ax.set_title(f"Boxplot — {column}", fontsize=14, pad=12)
    ax.set_ylabel(column, fontsize=12)
    ax.tick_params(labelsize=11)
    fig.tight_layout()
    return fig


# ── Nuage de points — PETIT, polices réduites ─────────────────────────────────

def plot_scatter(df: pd.DataFrame, col_x: str, col_y: str) -> plt.Figure:
    color     = _col_color(col_x)
    reg_color = _col_color(col_y)
    fig, ax = plt.subplots(figsize=(6, 4))           # PETIT
    fig.patch.set_facecolor(PALETTE["background"])
    ax.scatter(df[col_x], df[col_y],
               alpha=0.50, color=color, s=14, edgecolors="none")
    valid = df[[col_x, col_y]].dropna()
    if len(valid) > 1:
        m, b = np.polyfit(valid[col_x], valid[col_y], 1)
        ax.plot(valid[col_x], m * valid[col_x] + b,
                color=reg_color, linewidth=1.3, linestyle="--", alpha=0.85)
    ax.set_title(f"{col_x} vs {col_y}", fontsize=8, pad=5)  # police réduite
    ax.set_xlabel(col_x, fontsize=7)
    ax.set_ylabel(col_y, fontsize=7)
    ax.tick_params(labelsize=6)
    fig.tight_layout()
    return fig


# ── Heatmap corrélation — taille et polices adaptatives ───────────────────────

def plot_corr_matrix(corr: pd.DataFrame) -> plt.Figure:
    n = corr.shape[0]

    # Paliers: figure + toutes les polices réduites
    if n <= 4:
        fw, fh       = 5.0, 4.5
        annot_fs     = 9;  tick_fs = 8;  title_fs = 9;  cbar_fs = 7
        cbar_shrink  = 0.52
    elif n <= 7:
        fw, fh       = 7.0, 6.0
        annot_fs     = 8;  tick_fs = 7;  title_fs = 8;  cbar_fs = 6
        cbar_shrink  = 0.50
    elif n <= 12:
        fw, fh       = 9.5, 8.0
        annot_fs     = 7;  tick_fs = 6;  title_fs = 7;  cbar_fs = 6
        cbar_shrink  = 0.45
    else:
        fw   = min(n * 0.85, 20)
        fh   = min(n * 0.72, 17)
        annot_fs     = max(4, 7  - (n - 12) // 3)
        tick_fs      = max(4, 6  - (n - 12) // 4)
        title_fs     = max(5, 7  - (n - 12) // 4)
        cbar_fs      = max(4, 6  - (n - 12) // 4)
        cbar_shrink  = 0.40

    fig, ax = plt.subplots(figsize=(fw, fh))
    fig.patch.set_facecolor(PALETTE["background"])
    ax.set_facecolor(PALETTE["background"])

    mask = np.zeros_like(corr, dtype=bool)
    mask[np.triu_indices_from(mask, k=1)] = True

    cmap = sns.diverging_palette(270, 30, s=60, l=70, as_cmap=True)

    sns.heatmap(
        corr, mask=mask, cmap=cmap,
        annot=True, fmt=".2f",
        vmax=1.0, vmin=-1.0, center=0,
        square=True, linewidths=0.3, linecolor="white",
        annot_kws={"size": annot_fs, "color": PALETTE["text"]},
        cbar_kws={"shrink": cbar_shrink},
        ax=ax,
    )
    ax.set_title("Matrice de correlation", fontsize=title_fs, pad=8)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right", fontsize=tick_fs)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=tick_fs)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=cbar_fs)
    cbar.set_label("Correlation", fontsize=cbar_fs)
    fig.tight_layout()
    return fig


# ── Bar chart ─────────────────────────────────────────────────────────────────

def plot_bar(df: pd.DataFrame, column: str, top_n: int = 20) -> plt.Figure:
    vc = df[column].value_counts(dropna=False).head(top_n)
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(PALETTE["background"])
    ax.bar(range(len(vc)), vc.values,
           color=_cycle_n(len(vc)), edgecolor="white", linewidth=0.8)
    ax.set_xticks(range(len(vc)))
    ax.set_xticklabels(vc.index.astype(str), rotation=30, ha="right", fontsize=9)
    ax.set_title(f"Distribution — {column}", fontsize=13)
    ax.set_xlabel(column, fontsize=11)
    ax.set_ylabel("Effectif", fontsize=11)
    fig.tight_layout()
    return fig


# ── Pie chart ─────────────────────────────────────────────────────────────────

def plot_pie(df: pd.DataFrame, column: str) -> plt.Figure:
    vc = df[column].value_counts(dropna=False)
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor(PALETTE["background"])
    ax.pie(
        vc.values, labels=vc.index.astype(str),
        autopct="%1.1f%%", startangle=90,
        colors=_cycle_n(len(vc)), pctdistance=0.82,
        wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
    )
    ax.set_title(f"Repartition — {column}", fontsize=13)
    fig.tight_layout()
    return fig


# ── Boxplot groupé — GRAND ────────────────────────────────────────────────────

def plot_boxplot_by_cat(df: pd.DataFrame, num_col: str, cat_col: str) -> plt.Figure:
    order   = df[cat_col].value_counts().index.tolist()[:15]
    palette = {cat: _cycle_n(len(order))[i] for i, cat in enumerate(order)}
    fig, ax = plt.subplots(figsize=(13, 7))          # GRAND
    fig.patch.set_facecolor(PALETTE["background"])
    sns.boxplot(data=df, x=cat_col, y=num_col, order=order,
                palette=palette, linewidth=1.4, ax=ax)
    ax.set_title(f"{num_col} par {cat_col}", fontsize=14)
    ax.set_xlabel(cat_col, fontsize=11)
    ax.set_ylabel(num_col, fontsize=11)
    ax.tick_params(axis="x", rotation=30, labelsize=10)
    ax.tick_params(axis="y", labelsize=10)
    fig.tight_layout()
    return fig


# ── Violin plot — GRAND ───────────────────────────────────────────────────────

def plot_violin_by_cat(df: pd.DataFrame, num_col: str, cat_col: str) -> plt.Figure:
    order   = df[cat_col].value_counts().index.tolist()[:15]
    palette = {cat: _cycle_n(len(order))[i] for i, cat in enumerate(order)}
    fig, ax = plt.subplots(figsize=(13, 7))          # GRAND
    fig.patch.set_facecolor(PALETTE["background"])
    sns.violinplot(data=df, x=cat_col, y=num_col, order=order,
                   palette=palette, linewidth=1.2, ax=ax)
    ax.set_title(f"Violin — {num_col} par {cat_col}", fontsize=14)
    ax.set_xlabel(cat_col, fontsize=11)
    ax.set_ylabel(num_col, fontsize=11)
    ax.tick_params(axis="x", rotation=30, labelsize=10)
    ax.tick_params(axis="y", labelsize=10)
    fig.tight_layout()
    return fig
