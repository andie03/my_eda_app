# config.py — Global configuration constants

# Correlation threshold above which a correlation is considered "strong"
STRONG_CORR_THRESHOLD = 0.7

# Variance threshold below which a column is considered "low variance"
LOW_VARIANCE_THRESHOLD = 0.01

# Pastel color palette
PALETTE = {
    "primary":    "#B5A5D5",   # violet pastel
    "secondary":  "#A8C8E8",   # bleu pastel
    "accent":     "#F5E47A",   # jaune poussin pastel
    "mauve":      "#D4A8C8",   # mauve pastel
    "mint":       "#A8D5B5",   # menthe pastel
    "peach":      "#F5C8A8",   # peche pastel
    "neutral":    "#C0C0C8",
    "background": "#F7F7F7",
    "text":       "#2D2D2D",
}

# Rich pastel cycle — shuffled for visual variety across variables
PASTEL_CYCLE = [
    "#B5A5D5",  # violet pastel
    "#F5E47A",  # jaune poussin pastel
    "#A8D5B5",  # vert menthe pastel
    "#D4A8C8",  # mauve pastel
    "#A8C8E8",  # bleu ciel pastel
    "#F5C8A8",  # peche pastel
    "#C8E8A8",  # vert pomme pastel
    "#E8A8C8",  # rose pastel
    "#A8E8D5",  # turquoise pastel
    "#D5C8A8",  # sable pastel
    "#C8A8E8",  # lavande pastel
    "#E8D5A8",  # champagne pastel
    "#A8C8A8",  # vert sauge pastel
    "#E8B8A8",  # corail pastel
    "#B8D8E8",  # bleu pervenche pastel
    "#D8E8A8",  # citron pastel
]

# Diverging colormap for correlation matrix
CORR_PALETTE = "PuOr_r"

# Seaborn named palette for multi-series charts
MULTI_PALETTE = "pastel"

# Maximum number of categories for pie chart
PIE_MAX_CATEGORIES = 4

# Default figure DPI for PNG exports
EXPORT_DPI = 150

# Maximum rows displayed in preview
PREVIEW_ROWS = 10
