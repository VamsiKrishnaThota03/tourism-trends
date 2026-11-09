from pathlib import Path

from data_processor import TourismDataProcessor
from visualizer import TourismVisualizer

# Resolve data/ and output/ relative to the repository, not the current directory.
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"


def main():
    # Initialize components
    data_processor = TourismDataProcessor(data_dir=str(DATA_DIR))
    visualizer = TourismVisualizer(output_dir=str(OUTPUT_DIR))
    
    try:
        # Load and process data
        print("Loading tourism data...")
        data_processor.load_data("tourism_data.csv")
        
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
        data_processor.export_for_tableau(output_dir=str(OUTPUT_DIR))
        
        print(f"\nAnalysis complete! Check {OUTPUT_DIR} for:")
        print("1. Interactive HTML visualizations")
        print("2. CSV files ready for Tableau import")
        
    except FileNotFoundError:
        print(f"Error: tourism_data.csv not found in {DATA_DIR}.")
        print("Please ensure your data file is in the correct format and location.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 