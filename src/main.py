import os
from data_processor import TourismDataProcessor
from visualizer import TourismVisualizer
import pandas as pd
from typing import Dict

def main():
    # Initialize components
    data_processor = TourismDataProcessor()
    visualizer = TourismVisualizer()
    
    try:
        # Load and process data
        print("Loading tourism data...")
        data = data_processor.load_data("tourism_data.csv")
        
        # Process data for different views
        print("Processing data...")
        data_dict = {
            'yearly_trends': data_processor.get_yearly_trends(),
            'regional_comparison': data_processor.get_regional_comparison(),
            'visitor_demographics': data_processor.get_visitor_demographics(),
            'seasonal_patterns': data_processor.get_seasonal_patterns(),
            'top_destinations': data_processor.get_top_destinations()
        }
        
        # Create visualizations
        print("Creating visualizations...")
        visualizer.create_dashboard(data_dict)
        
        # Export data for Tableau
        print("Exporting data for Tableau...")
        data_processor.export_for_tableau()
        
        print("\nAnalysis complete! Check the 'output' directory for:")
        print("1. Interactive HTML visualizations")
        print("2. CSV files ready for Tableau import")
        
    except FileNotFoundError:
        print("Error: tourism_data.csv not found in the data directory.")
        print("Please ensure your data file is in the correct format and location.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 