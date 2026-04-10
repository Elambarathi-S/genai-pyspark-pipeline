"""
Run Analytics with Pandas (No Java Required)

This is a fallback demo script that performs similar analytics to the 
PySpark version but using Pandas instead. It doesn't require Java.

For the full PySpark version, install Java and run: python run_analytics.py
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from time import time

import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config


def setup_logging() -> None:
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main() -> None:
    """Main execution of analytics pipeline."""
    logger = logging.getLogger(__name__)
    
    print_section("E-COMMERCE SALES ANALYTICS (Pandas Demo)")
    print("Note: This uses Pandas for demo purposes. For production, install Java and use run_analytics.py\n")
    
    overall_start = time()
    
    try:
        # Load data
        print("📂 Loading Parquet files from data/raw/...")
        load_start = time()
        
        print("   → Loading customers.parquet...")
        customers_df = pd.read_parquet("data/raw/customers.parquet")
        
        print("   → Loading products.parquet...")
        products_df = pd.read_parquet("data/raw/products.parquet")
        
        print("   → Loading orders.parquet...")
        orders_df = pd.read_parquet("data/raw/orders.parquet")
        
        load_time = time() - load_start
        print(f"   ✓ Data loading completed in {load_time:.2f}s")
        print(f"     Customers: {len(customers_df):,} rows")
        print(f"     Products: {len(products_df):,} rows")
        print(f"     Orders: {len(orders_df):,} rows\n")
        
        # Analytics 1: Top Customers by Revenue
        print_section("1️⃣  TOP CUSTOMERS BY REVENUE")
        print("Calculating top 10 customers by total revenue spent...\n")
        
        top_customers_start = time()
        
        # Merge orders with products to get pricing
        orders_with_price = orders_df.merge(
            products_df[['product_id', 'price']], 
            on='product_id',
            how='inner'
        )
        
        # Calculate revenue
        orders_with_price['revenue'] = orders_with_price['quantity'] * orders_with_price['price']
        
        # Group by customer
        top_customers = orders_with_price.groupby('customer_id').agg({
            'revenue': 'sum',
            'order_id': 'count',
        }).reset_index()
        top_customers.columns = ['customer_id', 'total_revenue', 'num_orders']
        top_customers['avg_order_value'] = top_customers['total_revenue'] / top_customers['num_orders']
        top_customers = top_customers.sort_values('total_revenue', ascending=False).head(10)
        
        top_customers_time = time() - top_customers_start
        
        print(top_customers.to_string(index=False))
        print(f"\n⏱️  Execution time: {top_customers_time:.2f}s")
        
        # Analytics 2: Sales by Category
        print_section("2️⃣  SALES BY CATEGORY")
        print("Aggregating sales metrics by product category...\n")
        
        category_start = time()
        
        # Merge orders with products for category and pricing
        orders_with_category = orders_df.merge(
            products_df[['product_id', 'category', 'price']], 
            on='product_id',
            how='inner'
        )
        
        # Calculate revenue
        orders_with_category['revenue'] = orders_with_category['quantity'] * orders_with_category['price']
        
        # Group by category
        category_sales = orders_with_category.groupby('category').agg({
            'revenue': 'sum',
            'quantity': 'sum',
            'order_id': 'count',
        }).reset_index()
        category_sales.columns = ['category', 'total_revenue', 'total_units_sold', 'num_transactions']
        category_sales['avg_transaction_value'] = category_sales['total_revenue'] / category_sales['num_transactions']
        category_sales = category_sales.sort_values('total_revenue', ascending=False)
        
        category_time = time() - category_start
        
        print(category_sales.to_string(index=False))
        print(f"\n⏱️  Execution time: {category_time:.2f}s")
        
        # Analytics 3: Monthly Trends
        print_section("3️⃣  MONTHLY REVENUE TRENDS")
        print("Calculating month-over-month revenue growth...\n")
        
        trends_start = time()
        
        # Merge orders with products for pricing
        orders_with_price = orders_df.merge(
            products_df[['product_id', 'price']], 
            on='product_id',
            how='inner'
        )
        
        # Calculate revenue
        orders_with_price['revenue'] = orders_with_price['quantity'] * orders_with_price['price']
        
        # Extract year-month
        orders_with_price['order_date'] = pd.to_datetime(orders_with_price['order_date'])
        orders_with_price['year_month'] = orders_with_price['order_date'].dt.to_period('M')
        
        # Group by month and sum revenue
        monthly_revenue = orders_with_price.groupby('year_month')['revenue'].sum().reset_index()
        monthly_revenue.columns = ['year_month', 'total_revenue']
        
        # Calculate previous month revenue and growth
        monthly_revenue['prev_revenue'] = monthly_revenue['total_revenue'].shift(1)
        monthly_revenue['growth_percentage'] = (
            (monthly_revenue['total_revenue'] - monthly_revenue['prev_revenue']) / 
            monthly_revenue['prev_revenue'] * 100
        ).round(2)
        
        # Fill NaN for first month
        monthly_revenue['prev_revenue'] = monthly_revenue['prev_revenue'].fillna(0)
        monthly_revenue['growth_percentage'] = monthly_revenue['growth_percentage'].fillna(None)
        
        # Convert year_month to string for display
        monthly_revenue['year_month'] = monthly_revenue['year_month'].astype(str) + "-01"
        
        trends_time = time() - trends_start
        
        print(monthly_revenue.head(20).to_string(index=False))
        print(f"\n⏱️  Execution time: {trends_time:.2f}s")
        
        # Summary
        print_section("EXECUTION SUMMARY")
        print(f"Data Loading:        {load_time:>8.2f}s")
        print(f"Top Customers:       {top_customers_time:>8.2f}s")
        print(f"Category Sales:      {category_time:>8.2f}s")
        print(f"Monthly Trends:      {trends_time:>8.2f}s")
        print("-" * 35)
        
        total_analytics_time = top_customers_time + category_time + trends_time
        overall_time = time() - overall_start
        
        print(f"Total Analytics:     {total_analytics_time:>8.2f}s")
        print(f"Total Time:          {overall_time:>8.2f}s")
        
        print_section("ANALYTICS COMPLETE ✅")
        print("For PySpark distributed computing version:")
        print("  1. Install Java (JDK 8+)")
        print("  2. Set JAVA_HOME environment variable")
        print("  3. Run: python run_analytics.py\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure data files exist:")
        print("  - data/raw/customers.parquet")
        print("  - data/raw/products.parquet")
        print("  - data/raw/orders.parquet")
        print("\nGenerate them by running: python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Analytics execution failed")
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()
