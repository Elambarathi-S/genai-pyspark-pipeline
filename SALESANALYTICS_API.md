"""
Quick Reference for SalesAnalytics Class.

This file provides a quick API reference for the SalesAnalytics class
with common usage patterns and examples.
"""

# ============================================================================
# INITIALIZATION
# ============================================================================

from src.spark_analytics import SalesAnalytics

# Basic initialization
analytics = SalesAnalytics()

# With custom app name
analytics = SalesAnalytics(app_name="MyCustomApp")

# Using context manager (recommended for cleanup)
with SalesAnalytics() as analytics:
    # Your analytics code here
    pass


# ============================================================================
# LOADING DATA
# ============================================================================

# Load Parquet files into DataFrames
customers_df = analytics.load_parquet("data/raw/customers.parquet")
products_df = analytics.load_parquet("data/raw/products.parquet")
orders_df = analytics.load_parquet("data/raw/orders.parquet")


# ============================================================================
# ANALYTICS METHODS
# ============================================================================

# 1. TOP CUSTOMERS BY REVENUE
# Returns top N customers sorted by total revenue spent
top_customers = analytics.top_customers_by_revenue(
    orders_df=orders_df,
    products_df=products_df,
    n=10  # Get top 10 customers
)
top_customers.show()  # Display results

# Returns columns:
# - customer_id: Unique customer identifier
# - total_revenue: Total amount spent by customer (2 decimals)
# - num_orders: Number of orders placed
# - avg_order_value: Average revenue per order (2 decimals)


# 2. SALES BY CATEGORY
# Aggregates revenue and units sold by product category
category_sales = analytics.sales_by_category(
    orders_df=orders_df,
    products_df=products_df
)
category_sales.show()  # Display results

# Returns columns:
# - category: Product category name
# - total_revenue: Total revenue for category (2 decimals)
# - total_units_sold: Total units sold in category
# - num_transactions: Number of transactions in category
# - avg_transaction_value: Average transaction value (2 decimals)


# 3. MONTHLY TRENDS
# Calculates month-over-month revenue growth using Window functions
monthly_trends = analytics.monthly_trends(
    orders_df=orders_df,
    products_df=products_df
)
monthly_trends.show()  # Display results

# Returns columns:
# - year_month: Year and month as string (YYYY-MM-DD format)
# - total_revenue: Total revenue for month (2 decimals)
# - prev_revenue: Total revenue for previous month (2 decimals)
# - growth_percentage: Month-over-month growth percentage
#   (None for first month, formatted to 2 decimals)


# ============================================================================
# SPARK SESSION MANAGEMENT
# ============================================================================

# Get the configured Spark session
spark = analytics.create_spark_session()

# Get current Spark configuration
config = analytics.get_spark_config()
print(f"Executor Memory: {config.get('spark.executor.memory')}")
print(f"Serializer: {config.get('spark.serializer')}")

# Stop the Spark session
analytics.stop()  # Optional - context manager handles this automatically


# ============================================================================
# COMPLETE EXAMPLE
# ============================================================================

from src.spark_analytics import SalesAnalytics

def analyze_sales():
    """Complete analytics workflow example."""
    with SalesAnalytics(app_name="SalesAnalysis") as analytics:
        # Load data
        orders = analytics.load_parquet("data/raw/orders.parquet")
        products = analytics.load_parquet("data/raw/products.parquet")
        
        # Analyze
        top_10 = analytics.top_customers_by_revenue(orders, products, n=10)
        categories = analytics.sales_by_category(orders, products)
        trends = analytics.monthly_trends(orders, products)
        
        # Display results
        print("Top 10 Customers:")
        top_10.show()
        
        print("\nSales by Category:")
        categories.show()
        
        print("\nMonthly Trends:")
        trends.show()
        
        # Save results to Parquet (optional)
        top_10.write.parquet("data/output/top_customers.parquet", mode="overwrite")
        categories.write.parquet("data/output/category_sales.parquet", mode="overwrite")
        trends.write.parquet("data/output/monthly_trends.parquet", mode="overwrite")


# ============================================================================
# CONFIGURATION DETAILS
# ============================================================================

"""
Default Spark Configuration:
- spark.executor.memory: 4g
- spark.driver.memory: 4g
- spark.serializer: org.apache.spark.serializer.KryoSerializer
- spark.kryoserializer.buffer.max: 512m
- spark.sql.adaptive.enabled: true
  - spark.sql.adaptive.coalescePartitions.enabled: true
  - spark.sql.adaptive.skewJoin.enabled: true
- spark.sql.shuffle.partitions: 4
- spark.master: local[4]

These settings are optimized for local development and testing.
For production, adjust memory and partition settings based on your hardware.
"""


# ============================================================================
# ERROR HANDLING
# ============================================================================

from src.spark_analytics import SalesAnalytics

try:
    analytics = SalesAnalytics()
    df = analytics.load_parquet("data/raw/orders.parquet")
    result = analytics.top_customers_by_revenue(df, products_df)
    result.show()
except FileNotFoundError as e:
    print(f"Data file not found: {e}")
except Exception as e:
    print(f"Analytics error: {e}")
finally:
    analytics.stop()


# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

"""
1. Use context manager for automatic cleanup:
   with SalesAnalytics() as analytics:
       result = analytics.top_customers_by_revenue(...)

2. When performing multiple analyses, reuse DataFrames:
   orders = analytics.load_parquet("...")
   result1 = analytics.top_customers_by_revenue(orders, products)
   result2 = analytics.sales_by_category(orders, products)
   # Both reuse the same orders DataFrame (cached in Spark)

3. For large datasets, use limit() to sample results:
   top_customers.limit(100).show()

4. Convert to Pandas for further analysis:
   pdf = result.toPandas()
   # Now use pandas operations on pdf

5. Write results to Parquet for persistence:
   result.write.parquet("output_path", mode="overwrite")
   result.write.option("compression", "snappy").parquet("output_path")

6. Use Spark's native functions instead of iterating:
   # Good: result.select("column").distinct().count()
   # Bad: for row in result.collect(): ...
"""


# ============================================================================
# WINDOW FUNCTIONS EXPLANATION (used in monthly_trends)
# ============================================================================

"""
Window functions in monthly_trends():

The lag() function is used to get the previous month's revenue:

    lag("total_revenue").over(window_spec)

Window specification: Window.orderBy("year_month")
- Orders rows by year_month chronologically
- lag() returns the previous row's value
- First row returns None (no previous month)

This enables growth_percentage calculation:
    ((current_revenue - previous_revenue) / previous_revenue) * 100

Example output:
    year_month    | total_revenue | prev_revenue | growth_percentage
    2024-01-01    | 50000.00      | 0.00         | NULL
    2024-02-01    | 55000.00      | 50000.00     | 10.00
    2024-03-01    | 60500.00      | 55000.00     | 10.00
"""
