import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
import os

class TourismVisualizer:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_yearly_trend_plot(self, data: pd.DataFrame) -> go.Figure:
        """Create interactive yearly trend visualization."""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['Year'],
            y=data['Total_Visitors'],
            name='Total Visitors',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=data['Year'],
            y=data['Countries_Visited'],
            name='Countries Visited',
            line=dict(color='red'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Yearly Tourism Trends',
            xaxis_title='Year',
            yaxis_title='Total Visitors',
            yaxis2=dict(
                title='Countries Visited',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        
        return fig
    
    def create_regional_comparison(self, data: pd.DataFrame) -> go.Figure:
        """Create regional comparison visualization."""
        fig = px.bar(
            data,
            x='Region',
            y='Total_Visitors',
            color='Countries_Count',
            title='Regional Tourism Comparison',
            labels={
                'Total_Visitors': 'Total Visitors',
                'Countries_Count': 'Number of Countries'
            }
        )
        
        fig.update_layout(
            xaxis_title='Region',
            yaxis_title='Total Visitors',
            showlegend=True
        )
        
        return fig
    
    def create_demographics_heatmap(self, data: pd.DataFrame) -> go.Figure:
        """Create demographics heatmap visualization."""
        pivot_data = data.pivot(
            index='Age_Group',
            columns='Visitor_Type',
            values='Visitor_Count'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='Viridis'
        ))
        
        fig.update_layout(
            title='Visitor Demographics Heatmap',
            xaxis_title='Visitor Type',
            yaxis_title='Age Group'
        )
        
        return fig
    
    def create_seasonal_pattern_plot(self, data: pd.DataFrame) -> go.Figure:
        """Create seasonal pattern visualization."""
        fig = px.line(
            data,
            x='Year',
            y='Visitor_Count',
            color='Season',
            title='Seasonal Tourism Patterns',
            markers=True
        )
        
        fig.update_layout(
            xaxis_title='Year',
            yaxis_title='Visitor Count',
            hovermode='x unified'
        )
        
        return fig
    
    def create_top_destinations_plot(self, data: pd.DataFrame) -> go.Figure:
        """Create top destinations visualization."""
        fig = px.bar(
            data,
            x='Country',
            y='Visitor_Count',
            title='Top Tourist Destinations',
            color='Visitor_Count',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_title='Country',
            yaxis_title='Visitor Count',
            xaxis_tickangle=-45
        )
        
        return fig
    
    def save_visualization(self, fig: go.Figure, filename: str) -> None:
        """Save visualization to HTML file."""
        file_path = os.path.join(self.output_dir, filename)
        fig.write_html(file_path)
    
    def create_dashboard(self, data_dict: Dict[str, pd.DataFrame]) -> None:
        """Create and save all visualizations for the dashboard."""
        # Yearly trends
        yearly_trend_fig = self.create_yearly_trend_plot(data_dict['yearly_trends'])
        self.save_visualization(yearly_trend_fig, 'yearly_trends.html')
        
        # Regional comparison
        regional_fig = self.create_regional_comparison(data_dict['regional_comparison'])
        self.save_visualization(regional_fig, 'regional_comparison.html')
        
        # Demographics
        demographics_fig = self.create_demographics_heatmap(data_dict['visitor_demographics'])
        self.save_visualization(demographics_fig, 'demographics.html')
        
        # Seasonal patterns
        seasonal_fig = self.create_seasonal_pattern_plot(data_dict['seasonal_patterns'])
        self.save_visualization(seasonal_fig, 'seasonal_patterns.html')
        
        # Top destinations
        destinations_fig = self.create_top_destinations_plot(data_dict['top_destinations'])
        self.save_visualization(destinations_fig, 'top_destinations.html') 