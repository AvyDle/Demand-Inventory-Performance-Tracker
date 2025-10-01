"""
S&OP Visualization Module
========================

Advanced visualization utilities for Sales & Operations Planning analytics.

Functions:
- Executive dashboard creation
- Forecast accuracy visualization
- Regional performance analysis
- Inventory optimization charts
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Tuple

# Set visualization style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# AD Solutions color scheme
AD_COLORS = {
    'primary': '#CC5500',
    'secondary': '#B8470B', 
    'accent': '#FF6347',
    'highlight': '#FFA500',
    'neutral': '#8B4513'
}

def create_sop_dashboard(datasets: Dict[str, pd.DataFrame], figsize: Tuple[int,int]=(20,15)) -> plt.Figure:
    orders_df = datasets['orders']
    inventory_df = datasets['inventory']
    forecasts_df = datasets['forecasts']

    fig, axes = plt.subplots(3, 3, figsize=figsize)
    fig.suptitle('🔥 S&OP Executive Dashboard - AD Solutions', fontsize=20, fontweight='bold', y=0.95)

    segment_revenue = orders_df.groupby('customer_type')['order_value'].sum()
    axes[0, 0].pie(segment_revenue.values, labels=segment_revenue.index, autopct='%1.1f%%', colors=[AD_COLORS['primary'], AD_COLORS['secondary'], AD_COLORS['accent']])
    axes[0, 0].set_title('Customer Segment Revenue Distribution', fontweight='bold')

    regional_revenue = orders_df.groupby('region')['order_value'].sum().sort_values(ascending=True)
    axes[0, 1].barh(regional_revenue.index, regional_revenue.values, color=AD_COLORS['highlight'])
    axes[0, 1].set_title('Revenue by Region', fontweight='bold')
    axes[0, 1].set_xlabel('Revenue (R)')

    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    monthly_revenue = orders_df.groupby(orders_df['order_date'].dt.to_period('M'))['order_value'].sum()
    axes[0, 2].plot(monthly_revenue.index.astype(str), monthly_revenue.values, marker='o', color=AD_COLORS['primary'], linewidth=3)
    axes[0, 2].set_title('Monthly Revenue Trend', fontweight='bold')
    axes[0, 2].tick_params(axis='x', rotation=45)

    forecasts_df['absolute_error'] = abs(forecasts_df['variance_pct'])
    accuracy_by_type = 100 - forecasts_df.groupby('forecast_type')['absolute_error'].mean()
    axes[1, 0].bar(accuracy_by_type.index, accuracy_by_type.values, color=[AD_COLORS['secondary'], AD_COLORS['accent'], AD_COLORS['highlight']])
    axes[1, 0].set_title('Forecast Accuracy by Type', fontweight='bold')
    axes[1, 0].set_ylabel('Accuracy (%)')
    axes[1, 0].tick_params(axis='x', rotation=45)

    stock_status = inventory_df['stock_status'].value_counts()
    axes[1, 1].bar(stock_status.index, stock_status.values, color=[AD_COLORS['primary'], AD_COLORS['secondary'], AD_COLORS['accent']])
    axes[1, 1].set_title('Inventory Stock Status', fontweight='bold')
    axes[1, 1].set_ylabel('Number of Products')

    aov_by_segment = orders_df.groupby('customer_type')['order_value'].mean()
    axes[1, 2].bar(aov_by_segment.index, aov_by_segment.values, color=AD_COLORS['highlight'])
    axes[1, 2].set_title('Average Order Value by Segment', fontweight='bold')
    axes[1, 2].set_ylabel('AOV (R)')
    axes[1, 2].tick_params(axis='x', rotation=45)

    product_revenue = orders_df.groupby('product_id')['order_value'].sum().nlargest(10)
    axes[2, 0].barh(range(len(product_revenue)), product_revenue.values, color=AD_COLORS['secondary'])
    axes[2, 0].set_yticks(range(len(product_revenue)))
    axes[2, 0].set_yticklabels(product_revenue.index)
    axes[2, 0].set_title('Top 10 Products by Revenue', fontweight='bold')
    axes[2, 0].set_xlabel('Revenue (R)')

    axes[2, 1].hist(inventory_df['inventory_value'], bins=20, color=AD_COLORS['accent'], alpha=0.7, edgecolor='black')
    axes[2, 1].set_title('Inventory Value Distribution', fontweight='bold')
    axes[2, 1].set_xlabel('Inventory Value (R)')
    axes[2, 1].set_ylabel('Frequency')

    total_revenue = orders_df['order_value'].sum()
    total_orders = len(orders_df)
    forecast_accuracy = 100 - forecasts_df['absolute_error'].mean()
    inventory_value = inventory_df['inventory_value'].sum()

    metrics_text = f"""
    📊 S&OP KEY METRICS

    💰 Total Revenue: R{total_revenue:,.0f}
    📦 Total Orders: {total_orders:,}
    🎯 Forecast Accuracy: {forecast_accuracy:.1f}%
    📋 Inventory Value: R{inventory_value:,.0f}
    📈 AOV: R{total_revenue/total_orders:,.0f}
    """

    axes[2, 2].text(0.1, 0.5, metrics_text, fontsize=12, fontweight='bold', verticalalignment='center',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=AD_COLORS['highlight'], alpha=0.3))
    axes[2, 2].set_xlim(0, 1)
    axes[2, 2].set_ylim(0, 1)
    axes[2, 2].axis('off')

    plt.tight_layout()
    plt.subplots_adjust(top=0.92)

    return fig
