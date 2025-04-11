# Tourism Trends Analyzer

A comprehensive analysis tool for visualizing and understanding global tourism trends.

## Features

- Interactive dashboard for tourism data visualization
- Analysis of yearly trends and seasonal patterns
- Regional comparison of tourist destinations
- Visitor demographics analysis
- Export capabilities for Tableau integration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your tourism data CSV files in the `data` directory

3. Run the analysis:
```bash
python src/main.py
```

## Project Structure

- `src/` - Source code
  - `main.py` - Main application entry point
  - `data_processor.py` - Data processing and analysis
  - `visualizer.py` - Visualization components
- `data/` - Data directory for CSV files
- `output/` - Generated visualizations and reports

## Data Requirements

The system expects CSV files with the following columns:
- Year
- Country
- Region
- Visitor Count
- Visitor Type (Business/Leisure)
- Season
- Demographics (Age Groups)

## Output

The system generates:
1. Interactive web dashboard
2. CSV exports for Tableau
3. Static visualizations
4. Analysis reports 