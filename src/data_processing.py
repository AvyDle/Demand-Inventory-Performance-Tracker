"""
S&OP Data Processing Module
==========================

Comprehensive data processing utilities for Sales & Operations Planning analytics.

Functions:
- Data loading and validation
- Data cleaning and transformation
- Feature engineering
- Data quality checks
- Export utilities
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SOpDataProcessor:
    """
    Main class for S&OP data processing operations
    """
    
    def __init__(self):
        self.data_sources = {}
        self.processed_data = {}
        
    def load_datasets(self, file_paths: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """
        Load multiple CSV datasets
        
        Args:
            file_paths: Dictionary with dataset names as keys and file paths as values
            
        Returns:
            Dictionary of loaded DataFrames
        """
        loaded_data = {}
        
        for dataset_name, file_path in file_paths.items():
            try:
                df = pd.read_csv(file_path)
                loaded_data[dataset_name] = df
                logger.info(f"✅ Loaded {dataset_name}: {len(df):,} records")
            except FileNotFoundError:
                logger.error(f"❌ File not found: {file_path}")
                raise
            except Exception as e:
                logger.error(f"❌ Error loading {dataset_name}: {e}")
                raise
                
        self.data_sources = loaded_data
        return loaded_data
    
    def validate_data_quality(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, any]:
        """
        Perform comprehensive data quality checks
        
        Args:
            df: DataFrame to validate
            dataset_name: Name of the dataset for reporting
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'dataset_name': dataset_name,
            'total_records': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_records': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024*1024),
        }
        
        # Check for missing values by column
        missing_by_column = df.isnull().sum()
        validation_results['missing_by_column'] = missing_by_column[missing_by_column > 0].to_dict()
        
        # Check for negative values in numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        negative_values = {}
        for col in numeric_columns:
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                negative_values[col] = negative_count
        validation_results['negative_values'] = negative_values
        
        logger.info(f"📊 Data Quality Report for {dataset_name}:")
        logger.info(f"   Records: {validation_results['total_records']:,}")
        logger.info(f"   Missing Values: {validation_results['missing_values']:,}")
        logger.info(f"   Duplicates: {validation_results['duplicate_records']:,}")
        
        return validation_results
    
    def clean_orders_data(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and transform orders dataset
        """
        df = orders_df.copy()
        
        # Convert date columns
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # Create additional date features
        df['order_year'] = df['order_date'].dt.year
        df['order_month_num'] = df['order_date'].dt.month
        df['order_quarter'] = df['order_date'].dt.quarter
        df['order_week'] = df['order_date'].dt.isocalendar().week
        df['is_weekend'] = df['order_date'].dt.dayofweek.isin([5, 6])
        
        # Clean price and value columns
        numeric_columns = ['qty', 'base_price', 'unit_price', 'discount_pct', 'order_value']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove invalid orders
        initial_count = len(df)
        df = df[df['qty'] > 0]
        df = df[df['order_value'] > 0]
        df = df[df['unit_price'] > 0]
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.info(f"🧹 Removed {removed_count} invalid orders")
        
        # Calculate discount amount
        if 'discount_pct' in df.columns and 'base_price' in df.columns:
            df['discount_amount'] = df['base_price'] * (df['discount_pct'] / 100)
        
        # Revenue per unit
        df['revenue_per_unit'] = df['order_value'] / df['qty']
        
        logger.info(f"✅ Orders data cleaned: {len(df):,} records")
        return df
    
    def clean_inventory_data(self, inventory_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and transform inventory dataset
        """
        df = inventory_df.copy()
        
        # Clean numeric columns
        numeric_columns = ['available_qty', 'unit_cost', 'inventory_value', 'total_demand']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate inventory metrics
        df['days_of_supply'] = np.where(
            df['total_demand'] > 0,
            (df['available_qty'] / df['total_demand']) * 30,  # Assuming monthly demand
            np.inf
        )
        
        # Inventory turnover ratio
        df['turnover_ratio'] = np.where(
            df['inventory_value'] > 0,
            df['total_demand'] / df['inventory_value'],
            0
        )
        
        # Stock status validation
        valid_statuses = ['Excess', 'Adequate', 'Low']
        df['stock_status'] = df['stock_status'].where(
            df['stock_status'].isin(valid_statuses), 
            'Unknown'
        )
        
        # Remove invalid inventory records
        initial_count = len(df)
        df = df[df['available_qty'] >= 0]
        df = df[df['inventory_value'] >= 0]
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.info(f"🧹 Removed {removed_count} invalid inventory records")
        
        logger.info(f"✅ Inventory data cleaned: {len(df):,} records")
        return df
    
    def clean_forecasts_data(self, forecasts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and transform forecasts dataset
        """
        df = forecasts_df.copy()
        
        # Convert forecast_month to datetime
        df['forecast_month'] = pd.to_datetime(df['forecast_month'])
        
        # Clean numeric columns
        numeric_columns = ['forecast_qty', 'actual_demand', 'variance_pct']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate additional forecast metrics
        df['absolute_error'] = abs(df['variance_pct'])
        df['forecast_accuracy'] = 100 - df['absolute_error']
        
        # Categorize forecast performance
        df['accuracy_category'] = pd.cut(
            df['forecast_accuracy'],
            bins=[-np.inf, 70, 85, 95, np.inf],
            labels=['Poor', 'Fair', 'Good', 'Excellent']
        )
        
        # Validate forecast types
        valid_types = ['Manual', 'Statistical', 'ML_Model']
        df['forecast_type'] = df['forecast_type'].where(
            df['forecast_type'].isin(valid_types),
            'Unknown'
        )
        
        # Validate confidence levels
        valid_confidence = ['Low', 'Medium', 'High']
        df['confidence_level'] = df['confidence_level'].where(
            df['confidence_level'].isin(valid_confidence),
            'Unknown'
        )
        
        logger.info(f"✅ Forecasts data cleaned: {len(df):,} records")
        return df
    
    def clean_products_data(self, products_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and transform products dataset
        """
        df = products_df.copy()
        
        # Clean price columns
        df['base_price'] = pd.to_numeric(df['base_price'], errors='coerce')
        
        # Price categories
        df['price_category'] = pd.cut(
            df['base_price'],
            bins=[0, 1000, 5000, 15000, np.inf],
            labels=['Budget', 'Mid-Range', 'Premium', 'Luxury']
        )
        
        # Clean categorical columns
        valid_tiers = ['High', 'Medium', 'Low']
        df['promotional_tier'] = df['promotional_tier'].where(
            df['promotional_tier'].isin(valid_tiers),
            'Unknown'
        )
        
        df['demand_volatility'] = df['demand_volatility'].where(
            df['demand_volatility'].isin(valid_tiers),
            'Unknown'
        )
        
        # Create product name length feature
        df['product_name_length'] = df['product_name'].str.len()
        
        logger.info(f"✅ Products data cleaned: {len(df):,} records")
        return df
    
    def engineer_features(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Engineer additional features across datasets
        """
        enhanced_datasets = {}
        
        for name, df in datasets.items():
            enhanced_datasets[name] = df.copy()
        
        # Orders feature engineering
        if 'orders' in enhanced_datasets:
            orders_df = enhanced_datasets['orders']
            
            # Customer behavior features
            customer_stats = orders_df.groupby('customer_type').agg({
                'order_value': ['mean', 'std', 'count'],
                'discount_pct': 'mean'
            }).round(2)
            
            customer_stats.columns = ['avg_order_value', 'order_value_std', 'order_frequency', 'avg_discount']
            customer_stats = customer_stats.reset_index()
            
            # Merge back to orders
            orders_df = orders_df.merge(customer_stats, on='customer_type', how='left')
            
            # Product performance metrics
            product_stats = orders_df.groupby('product_id').agg({
                'order_value': ['sum', 'count'],
                'qty': 'sum'
            }).round(2)
            
            product_stats.columns = ['total_product_revenue', 'total_orders', 'total_qty_sold']
            product_stats = product_stats.reset_index()
            
            orders_df = orders_df.merge(product_stats, on='product_id', how='left')
            
            enhanced_datasets['orders'] = orders_df
        
        # Cross-dataset features
        if 'orders' in enhanced_datasets and 'inventory' in enhanced_datasets:
            orders_df = enhanced_datasets['orders']
            inventory_df = enhanced_datasets['inventory']
            
            # Product demand vs inventory
            demand_summary = orders_df.groupby('product_id').agg({
                'qty': 'sum',
                'order_value': 'sum'
            }).rename(columns={'qty': 'historical_demand', 'order_value': 'historical_revenue'})
            
            inventory_enhanced = inventory_df.merge(demand_summary, on='product_id', how='left')
            inventory_enhanced['demand_coverage_ratio'] = (
                inventory_enhanced['available_qty'] / inventory_enhanced['historical_demand'].fillna(1)
            )
            
            enhanced_datasets['inventory'] = inventory_enhanced
        
        logger.info("✅ Feature engineering completed")
        return enhanced_datasets
    
    def create_summary_statistics(self, datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Create comprehensive summary statistics
        """
        summary_stats = []
        
        for dataset_name, df in datasets.items():
            stats = {
                'dataset': dataset_name,
                'record_count': len(df),
                'column_count': len(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024*1024),
                'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
                'categorical_columns': len(df.select_dtypes(include=['object']).columns),
                'datetime_columns': len(df.select_dtypes(include=['datetime64']).columns),
                'missing_values': df.isnull().sum().sum(),
                'duplicate_rows': df.duplicated().sum()
            }
            
            # Dataset specific metrics
            if dataset_name == 'orders':
                stats['total_revenue'] = df['order_value'].sum() if 'order_value' in df.columns else 0
                stats['date_range'] = f"{df['order_date'].min()} to {df['order_date'].max()}" if 'order_date' in df.columns else 'N/A'
            elif dataset_name == 'inventory':
                stats['total_inventory_value'] = df['inventory_value'].sum() if 'inventory_value' in df.columns else 0
            elif dataset_name == 'forecasts':
                stats['avg_forecast_accuracy'] = (100 - df['absolute_error'].mean()) if 'absolute_error' in df.columns else 0
            
            summary_stats.append(stats)
        
        summary_df = pd.DataFrame(summary_stats)
        logger.info("📊 Summary statistics created")
        return summary_df
    
    def export_processed_data(self, datasets: Dict[str, pd.DataFrame], output_dir: str = './processed_data/') -> None:
        """
        Export processed datasets to CSV files
        """
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        for dataset_name, df in datasets.items():
            filename = f"{dataset_name}_processed.csv"
            filepath = os.path.join(output_dir, filename)
            
            df.to_csv(filepath, index=False)
            logger.info(f"💾 Exported {dataset_name}: {filepath}")
        
        logger.info(f"✅ All datasets exported to {output_dir}")

def process_sop_data(file_paths: Dict[str, str]) -> Dict[str, pd.DataFrame]:
    """
    Main function to process all S&OP datasets
    
    Args:
        file_paths: Dictionary with dataset names and file paths
        
    Returns:
        Dictionary of processed DataFrames
    """
    processor = SOpDataProcessor()
    
    # Load data
    logger.info("🔄 Starting S&OP data processing pipeline...")
    raw_data = processor.load_datasets(file_paths)
    
    # Validate data quality
    validation_results = {}
    for name, df in raw_data.items():
        validation_results[name] = processor.validate_data_quality(df, name)
    
    # Clean individual datasets
    cleaned_data = {}
    
    if 'orders' in raw_data:
        cleaned_data['orders'] = processor.clean_orders_data(raw_data['orders'])
    
    if 'inventory' in raw_data:
        cleaned_data['inventory'] = processor.clean_inventory_data(raw_data['inventory'])
        
    if 'forecasts' in raw_data:
        cleaned_data['forecasts'] = processor.clean_forecasts_data(raw_data['forecasts'])
        
    if 'products' in raw_data:
        cleaned_data['products'] = processor.clean_products_data(raw_data['products'])
    
    # Feature engineering
    enhanced_data = processor.engineer_features(cleaned_data)
    
    # Create summary statistics
    summary_stats = processor.create_summary_statistics(enhanced_data)
    print("\n" + "="*60)
    print("📊 DATA PROCESSING SUMMARY")
    print("="*60)
    print(summary_stats.to_string(index=False))
    
    logger.info("🎉 S&OP data processing pipeline completed successfully!")
    
    return enhanced_data

# Utility functions
def detect_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.Series:
    """
    Detect outliers in a numeric column
    
    Args:
        df: DataFrame
        column: Column name
        method: 'iqr' or 'zscore'
        
    Returns:
        Boolean series indicating outliers
    """
    if method == 'iqr':
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return (df[column] < lower_bound) | (df[column] > upper_bound)
    
    elif method == 'zscore':
        from scipy import stats
        z_scores = np.abs(stats.zscore(df[column].dropna()))
        return z_scores > 3
    
    else:
        raise ValueError("Method must be 'iqr' or 'zscore'")

def create_data_profile(df: pd.DataFrame, dataset_name: str) -> Dict[str, any]:
    """
    Create a comprehensive data profile
    """
    profile = {
        'dataset_name': dataset_name,
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_summary': df.isnull().sum().to_dict(),
        'numeric_summary': df.describe().to_dict(),
        'categorical_summary': {col: df[col].value_counts().head().to_dict() 
                              for col in df.select_dtypes(include=['object']).columns}
    }
    
    return profile

if __name__ == "__main__":
    # Example usage
    file_paths = {
        'orders': 'final_orders_perfect_integrity.csv',
        'products': 'final_products_perfect_integrity.csv', 
        'inventory': 'final_inventory_perfect_integrity.csv',
        'forecasts': 'final_forecasts_perfect_integrity.csv'
    }
    
    processed_datasets = process_sop_data(file_paths)
    print("\n🎯 Data processing completed! Datasets ready for analysis.")
