# Tourism Trends Analyzer

A Django web app for uploading tourism datasets and exploring them through interactive Plotly charts, with CSV export and a Web Data Connector for Tableau.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-3.2-092E20?logo=django&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?logo=plotly&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.1-150458?logo=pandas&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

## Overview

The project has two parts:

1. **Django dashboard** (`tourism_analyzer/` + `tourism_dashboard/`): logged-in users upload tourism CSVs, filter the data and view yearly, regional and visitor-type charts. They can also save custom chart definitions and export data for Tableau.
2. **Stand-alone analysis script** (`src/`): a pandas + Plotly pipeline that reads `data/tourism_data.csv` and writes interactive HTML charts and Tableau-ready CSVs to `output/`.

## Features

### Web dashboard

- **Authentication**: Django login/logout. Every dashboard page requires login.
- **CSV upload**: rows are parsed with pandas and stored as `TourismData` records linked to the uploading user
- **Interactive charts** (Plotly.js), fed by a JSON endpoint:
  - Yearly visitor trend (line)
  - Regional distribution (pie)
  - Visitors by type, Business vs Leisure (bar)
- **Filters**: year range, region and visitor type
- **Saved preferences**: each user's default view and filters (`UserDashboard`)
- **Custom visualizations**: save a title, chart type (line, bar, pie, scatter, heatmap) and JSON filter/config definitions, and delete them later
- **Tableau integration**
  - Download your data as CSV (`/export-tableau/`)
  - Paste a Tableau embed code to show a Tableau Public view on the page
  - A Tableau Web Data Connector endpoint (`/tableau-wdc/`) that returns the records as JSON
- **Django admin** at `/admin/`

### Analysis script (`src/main.py`)

- Yearly trends, regional comparison, visitor demographics (age group × visitor type), seasonal patterns and top-10 destinations
- Writes interactive Plotly HTML files and matching CSVs to `output/`

## Tech stack

- Python 3.11, Django 3.2
- pandas, NumPy
- Plotly (Python, in `src/`) and Plotly.js (CDN, dashboard)
- django-crispy-forms + crispy-bootstrap5, Bootstrap 5
- SQLite (Django default)
- Also in `requirements.txt`: `dash`, `django-plotly-dash`, `matplotlib`, `seaborn`, `python-dotenv`

## Project structure

```
tourism-trends/
├── manage.py
├── requirements.txt
├── tourism_analyzer/          # Django project: settings, root URLs, WSGI/ASGI
├── tourism_dashboard/         # Django app
│   ├── models.py              # TourismData, UserDashboard, CustomVisualization
│   ├── views.py               # Dashboard, upload, chart API, Tableau export/WDC
│   ├── forms.py
│   ├── urls.py
│   ├── migrations/
│   └── templates/             # Dashboard and Tableau templates
├── templates/tourism_dashboard/   # base, login, upload, create_visualization
├── src/                       # Stand-alone pandas/Plotly analysis
│   ├── main.py
│   ├── data_processor.py
│   └── visualizer.py
├── data/tourism_data.csv      # Sample dataset
├── sample_data.csv            # Second sample dataset for upload
└── output/                    # Generated HTML charts and CSVs from src/main.py
```

## Getting started

### Prerequisites

- Python 3.11 (Django 3.2 also runs on 3.8–3.10)

### Install

```bash
git clone https://github.com/VamsiKrishnaThota03/tourism-trends.git
cd tourism-trends

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run the web app

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/, log in, then go to **Upload Data** and upload `data/tourism_data.csv` or `sample_data.csv`.

### Run the analysis script

Run it from the repository root, because `data/` and `output/` are resolved relative to the current directory:

```bash
python src/main.py
```

### Configuration

The settings are currently hard-coded in `tourism_analyzer/settings.py` (`DEBUG = True`, SQLite). Before any deployment, move them to environment variables:

| Setting | Purpose | Example |
|---------|---------|---------|
| `SECRET_KEY` | Django cryptographic signing key | `<generate-a-new-secret-key>` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Hostnames the app may serve | `<your-domain>` |

## Data format

Uploaded CSVs must include these columns:

| Column | Example |
|--------|---------|
| `Year` | `2020` |
| `Country` | `France` |
| `Region` | `Europe` |
| `Visitor_Count` | `1500000` |
| `Visitor_Type` | `Business` / `Leisure` |
| `Season` | `Spring` |
| `Age_Group` | `18-24` |

## Endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `GET` | `/` | login | Dashboard |
| `GET`/`POST` | `/upload/` | login | Upload a CSV |
| `GET`/`POST` | `/create-visualization/` | login | Save a custom visualization |
| `POST` | `/update-preferences/` | login | Save default view and filters (JSON) |
| `GET` | `/delete-visualization/<id>/` | login | Delete a custom visualization |
| `GET` | `/api/visualization/<view_type>/` | none | Chart data as JSON (`?year_range=2020-2023&region=&visitor_type=`) |
| `GET` | `/export-tableau/` | login | Download your data as CSV |
| `GET` | `/tableau-dashboard/` | none | Tableau embed / instructions page |
| `GET`/`POST` | `/tableau-wdc/` | none | Tableau Web Data Connector page and data |
| `GET` | `/debug/data/` | none | Record counts (debug) |
| `GET`/`POST` | `/login/`, `/logout/` | n/a | Authentication |
| `GET` | `/admin/` | staff | Django admin |

## Contact

Thota Vamsi Krishna — [GitHub](https://github.com/VamsiKrishnaThota03)
