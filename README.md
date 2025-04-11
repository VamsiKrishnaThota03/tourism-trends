# Tourism Trends Analyzer

A comprehensive Django web application for analyzing and visualizing global tourism trends.

## Features

- Interactive dashboard with real-time data visualization
- Data upload functionality for CSV files
- Analysis of yearly trends, regional distribution, and visitor demographics
- Custom visualization creation
- Tableau integration for advanced analytics
- User authentication and data management

## Setup

1. Clone the repository:
```bash
git clone https://github.com/VamsiKrishnaThota03/tourism-trends.git
cd tourism-trends
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

7. Access the application at http://127.0.0.1:8000/

## Project Structure

- `tourism_analyzer/` - Main Django project directory
  - `settings.py` - Project settings
  - `urls.py` - Main URL routing
- `tourism_dashboard/` - Main application
  - `models.py` - Data models
  - `views.py` - View functions
  - `urls.py` - Application URL routing
  - `forms.py` - Form definitions
- `templates/` - HTML templates
  - `tourism_dashboard/` - Application templates
- `static/` - Static files (CSS, JavaScript, images)
- `data/` - Sample data files

## Data Requirements

The application accepts CSV files with the following columns:
- Year
- Country
- Region
- Visitor_Count
- Visitor_Type (Business/Leisure)
- Season
- Age_Group

## Features in Detail

### Dashboard
- Interactive visualizations of tourism trends
- Filtering by year range, region, and visitor type
- Real-time data updates

### Data Management
- Upload CSV files with tourism data
- View and manage uploaded datasets
- Data validation and error handling

### Visualization
- Yearly trends analysis
- Regional distribution charts
- Visitor demographics breakdown
- Custom visualization creation

### Tableau Integration
- Export data for Tableau
- Embed Tableau visualizations
- Direct connection via Web Data Connector

## Technologies Used

- Django 3.2
- Python 3.11
- Plotly.js for visualizations
- Bootstrap 5 for UI
- SQLite database (default)
- Tableau integration

## License

This project is licensed under the MIT License - see the LICENSE file for details. 