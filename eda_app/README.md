# EDA Explorer

Application d'analyse exploratoire de données (EDA) construite avec Streamlit.

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

## Structure du projet

```
eda_app/
├── app.py              # Point d'entree (upload, session_state, tabs)
├── config.py           # Constantes globales (palettes, seuils)
├── requirements.txt
│
├── services/           # Logique data (jamais de visuel ici)
│   ├── data_loader.py  # Chargement CSV avec cache
│   ├── preprocessing.py# NaN, doublons, faible variance
│   └── analysis.py     # Stats, IQR, correlations, contingence
│
├── visuals/            # Graphiques purs (data -> figure matplotlib)
│   └── plots.py
│
├── ui/                 # Interface Streamlit (connecte services + visuals)
│   ├── overview.py
│   ├── numeric.py
│   └── categorical.py
│
└── utils/
    ├── helpers.py      # Detection types, outils generiques
    └── export.py       # CSV, PNG, PDF
```

## Fonctionnalites

- **Overview** : apercu, types, valeurs manquantes, doublons, variance faible
- **Numerique** : stats descriptives, histogramme, boxplot, scatter, outliers IQR, matrice de correlation
- **Categoriel** : distribution, pie/bar selon le nombre de classes, analyse croisee boxplot + violin, table de contingence
- **Exports** : CSV sans index, PNG par graphique, rapport PDF simplifie
