import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os

class TourismDataProcessor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.data = None
        
    def load_data(self, filename: str) -> pd.DataFrame:
        """Load tourism data from CSV file."""
        file_path = os.path.join(self.data_dir, filename)
        self.data = pd.read_csv(file_path)
        return self.data
    
    def get_yearly_trends(self) -> pd.DataFrame:
        """Analyze yearly tourism trends."""
        if self.data is None:
            raise ValueError("No data loaded. Please load data first.")
        
        yearly_trends = self.data.groupby('Year').agg({
            'Visitor_Count': 'sum',
            'Country': 'nunique'
        }).reset_index()
        
        yearly_trends.columns = ['Year', 'Total_Visitors', 'Countries_Visited']
        return yearly_trends
    
    def get_regional_comparison(self) -> pd.DataFrame:
        """Compare tourism trends across regions."""
        if self.data is None:
            raise ValueError("No data loaded. Please load data first.")
        
        regional_stats = self.data.groupby('Region').agg({
            'Visitor_Count': 'sum',
            'Country': 'nunique'
        }).reset_index()
        
        regional_stats.columns = ['Region', 'Total_Visitors', 'Countries_Count']
        return regional_stats
    
    def get_visitor_demographics(self) -> pd.DataFrame:
        """Analyze visitor demographics."""
        if self.data is None:
            raise ValueError("No data loaded. Please load data first.")
        
        demographics = self.data.groupby(['Age_Group', 'Visitor_Type']).agg({
            'Visitor_Count': 'sum'
        }).reset_index()
        
        return demographics
    
    def get_seasonal_patterns(self) -> pd.DataFrame:
        """Analyze seasonal tourism patterns."""
        if self.data is None:
            raise ValueError("No data loaded. Please load data first.")
        
        seasonal_patterns = self.data.groupby(['Season', 'Year']).agg({
            'Visitor_Count': 'sum'
        }).reset_index()
        
        return seasonal_patterns
    
    def get_top_destinations(self, n: int = 10) -> pd.DataFrame:
        """Get top N tourist destinations."""
        if self.data is None:
            raise ValueError("No data loaded. Please load data first.")
        
        top_destinations = self.data.groupby('Country').agg({
            'Visitor_Count': 'sum'
        }).sort_values('Visitor_Count', ascending=False).head(n).reset_index()
        
        return top_destinations
    
    def export_for_tableau(self, output_dir: str = "output") -> None:
        """Export processed data for Tableau visualization."""
        if self.data is None:
            raise ValueError("No data loaded. Please load data first.")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Export various views for Tableau
        self.get_yearly_trends().to_csv(os.path.join(output_dir, 'yearly_trends.csv'), index=False)
        self.get_regional_comparison().to_csv(os.path.join(output_dir, 'regional_comparison.csv'), index=False)
        self.get_visitor_demographics().to_csv(os.path.join(output_dir, 'visitor_demographics.csv'), index=False)
        self.get_seasonal_patterns().to_csv(os.path.join(output_dir, 'seasonal_patterns.csv'), index=False)
        self.get_top_destinations().to_csv(os.path.join(output_dir, 'top_destinations.csv'), index=False) 