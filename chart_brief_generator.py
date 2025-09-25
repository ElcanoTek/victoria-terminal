#!/usr/bin/env python3
"""
Chart Brief Generator for Gamma AI

A utility tool to help generate structured chart briefs that improve
the quality of charts and visualizations created by Gamma AI.
"""

from typing import Dict, List, Any, Optional
from enum import Enum

class ChartType(Enum):
    BAR = "bar"
    COLUMN = "column"
    LINE = "line"
    PIE = "pie"
    DONUT = "donut"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    HEATMAP = "heatmap"
    AREA = "area"

class ChartBriefGenerator:
    """Generates structured chart briefs for Gamma AI presentations."""
    
    @staticmethod
    def generate_chart_brief(
        chart_type: ChartType,
        title: str,
        data: List[Dict[str, Any]],
        x_axis_title: Optional[str] = None,
        y_axis_title: Optional[str] = None,
        key_insight: Optional[str] = None,
        color_palette: str = "Elcano brand colors",
        sort_order: Optional[str] = None
    ) -> str:
        """
        Generate a structured chart brief for Gamma AI.
        
        Args:
            chart_type: The type of chart to create
            title: The chart title
            data: List of data dictionaries
            x_axis_title: Title for X-axis (optional)
            y_axis_title: Title for Y-axis (optional)
            key_insight: Key insight to highlight (optional)
            color_palette: Color palette to use
            sort_order: How to sort the data (optional)
            
        Returns:
            Formatted chart brief as markdown string
        """
        
        # Generate chart-specific instructions
        chart_instructions = ChartBriefGenerator._get_chart_instructions(chart_type)
        
        # Build the chart brief
        brief = f"""**Chart Brief:**
- **Chart Type**: {chart_instructions['type_name']}
- **Title**: "{title}"
"""
        
        if x_axis_title:
            brief += f"- **X-Axis Title**: \"{x_axis_title}\"\n"
        if y_axis_title:
            brief += f"- **Y-Axis Title**: \"{y_axis_title}\"\n"
            
        brief += f"- **Data Labels**: {chart_instructions['data_labels']}\n"
        
        if sort_order:
            brief += f"- **Sorting**: {sort_order}\n"
        elif chart_instructions['default_sort']:
            brief += f"- **Sorting**: {chart_instructions['default_sort']}\n"
            
        brief += f"- **Color Palette**: Use {color_palette}\n"
        brief += f"- **Purpose**: {chart_instructions['purpose']}\n"
        
        if key_insight:
            brief += f"- **Key Insight**: {key_insight}\n"
            
        # Add data table
        brief += "\n**Data:**\n"
        brief += ChartBriefGenerator._format_data_table(data)
        
        return brief
    
    @staticmethod
    def _get_chart_instructions(chart_type: ChartType) -> Dict[str, str]:
        """Get chart-specific instructions based on chart type."""
        
        instructions = {
            ChartType.BAR: {
                "type_name": "Horizontal Bar Chart",
                "purpose": "Compare values across different categories",
                "data_labels": "Show values on bars, formatted appropriately",
                "default_sort": "Sort bars from highest to lowest for easy comparison"
            },
            ChartType.COLUMN: {
                "type_name": "Vertical Column Chart", 
                "purpose": "Compare values across different categories",
                "data_labels": "Show values on top of columns, formatted appropriately",
                "default_sort": "Sort columns from highest to lowest for easy comparison"
            },
            ChartType.LINE: {
                "type_name": "Line Chart",
                "purpose": "Show trends and changes over time",
                "data_labels": "Add markers for each data point to improve readability",
                "default_sort": "Sort by time/sequence in chronological order"
            },
            ChartType.PIE: {
                "type_name": "Pie Chart",
                "purpose": "Show proportions of each category as part of the whole",
                "data_labels": "Label each slice with category name and percentage",
                "default_sort": "Sort slices from largest to smallest, limit to 5 categories max"
            },
            ChartType.DONUT: {
                "type_name": "Donut Chart",
                "purpose": "Show proportions with emphasis on the total in the center",
                "data_labels": "Label each segment with category name and percentage",
                "default_sort": "Sort segments from largest to smallest, limit to 5 categories max"
            },
            ChartType.SCATTER: {
                "type_name": "Scatter Plot",
                "purpose": "Show relationships and correlations between two variables",
                "data_labels": "Label key data points, include trendline if correlation exists",
                "default_sort": None
            },
            ChartType.BUBBLE: {
                "type_name": "Bubble Chart",
                "purpose": "Show relationships between three variables using position and size",
                "data_labels": "Label significant bubbles, use size to represent third variable",
                "default_sort": None
            },
            ChartType.HEATMAP: {
                "type_name": "Heatmap",
                "purpose": "Show patterns and intensity across two categorical dimensions",
                "data_labels": "Use color intensity to represent values, include legend",
                "default_sort": "Arrange categories logically (e.g., time, alphabetical)"
            },
            ChartType.AREA: {
                "type_name": "Area Chart",
                "purpose": "Show cumulative totals and trends over time",
                "data_labels": "Label key points and show total values",
                "default_sort": "Sort by time/sequence in chronological order"
            }
        }
        
        return instructions.get(chart_type, {
            "type_name": "Chart",
            "purpose": "Visualize the data effectively",
            "data_labels": "Include appropriate labels",
            "default_sort": None
        })
    
    @staticmethod
    def _format_data_table(data: List[Dict[str, Any]]) -> str:
        """Format data as a markdown table."""
        if not data:
            return "| No data provided |\n|---|\n"
            
        # Get headers from first row
        headers = list(data[0].keys())
        
        # Create table header
        table = "| " + " | ".join(headers) + " |\n"
        table += "|" + "|".join(["---"] * len(headers)) + "|\n"
        
        # Add data rows
        for row in data:
            values = [str(row.get(header, "")) for header in headers]
            table += "| " + " | ".join(values) + " |\n"
            
        return table

# Example usage functions
def create_campaign_performance_chart():
    """Example: Create a chart brief for campaign performance data."""
    
    data = [
        {"Platform": "Google Ads", "Spend": "$1,250,000", "CTR": "3.2%", "Conversions": "15,600"},
        {"Platform": "Facebook Ads", "Spend": "$750,000", "CTR": "2.8%", "Conversions": "9,800"},
        {"Platform": "LinkedIn Ads", "Spend": "$300,000", "CTR": "1.9%", "Conversions": "2,100"},
        {"Platform": "Twitter Ads", "Spend": "$150,000", "CTR": "1.5%", "Conversions": "800"}
    ]
    
    brief = ChartBriefGenerator.generate_chart_brief(
        chart_type=ChartType.BAR,
        title="Q4 2025 Campaign Performance by Platform",
        data=data,
        x_axis_title="Total Spend (USD)",
        y_axis_title="Advertising Platform",
        key_insight="Google Ads dominates spend with over 50% of total budget and highest conversion volume",
        sort_order="Sort bars by spend from highest to lowest"
    )
    
    return brief

def create_trend_analysis_chart():
    """Example: Create a chart brief for trend analysis."""
    
    data = [
        {"Month": "Jan 2025", "CTR": "2.1%", "CPC": "$0.45"},
        {"Month": "Feb 2025", "CTR": "2.3%", "CPC": "$0.42"},
        {"Month": "Mar 2025", "CTR": "2.8%", "CPC": "$0.38"},
        {"Month": "Apr 2025", "CTR": "3.1%", "CPC": "$0.35"}
    ]
    
    brief = ChartBriefGenerator.generate_chart_brief(
        chart_type=ChartType.LINE,
        title="Campaign Performance Trends - Q1 2025",
        data=data,
        x_axis_title="Month",
        y_axis_title="Click-Through Rate (%)",
        key_insight="CTR has improved consistently each month while CPC has decreased, indicating optimization success"
    )
    
    return brief

if __name__ == "__main__":
    # Test the chart brief generator
    print("=== Campaign Performance Chart Brief ===")
    print(create_campaign_performance_chart())
    print("\n=== Trend Analysis Chart Brief ===")
    print(create_trend_analysis_chart())
