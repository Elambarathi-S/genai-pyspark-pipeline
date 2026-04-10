"""
RUNNING THE ANALYTICS

This document explains how to run the SalesAnalytics demonstrations.
"""

# ============================================================================
# PREREQUISITES
# ============================================================================

"""
Before running analytics, ensure:

1. Data has been generated (Phase 4)
   Run: python main.py
   This creates data/raw/*.parquet files
   
2. Dependencies are installed
   Run: pip install -r requirements.txt
   Key package: pyspark==3.5.0
   
3. Python environment is ready
   Python 3.8+ with pip
"""


# ============================================================================
# RUN ANALYTICS DEMO
# ============================================================================

"""
Quick Start:
   python analytics_demo.py

What it does:
✅ Loads Parquet files (100K customers, 10K products, 1M orders)
✅ Initializes Spark session with optimized configuration
✅ Runs all 5 analytics methods
✅ Displays results
✅ Shows summary statistics
✅ Logs execution to logs/analytics_demo.log

Expected Output:
- 10 top customers by revenue
- Sales breakdown by category
- Monthly trends with growth %
- Overall statistics (customers, products, orders, total revenue)

Execution Time:
- First run: ~2-3 seconds (Spark startup)
- Analytics: ~15-20 seconds
- Total: ~20-25 seconds

Log File:
- Location: logs/analytics_demo.log
- Contains: Detailed execution trace
"""


# ============================================================================
# RUN UNIT TESTS
# ============================================================================

"""
Run all tests:
   pytest tests/test_spark_analytics.py -v

Run with coverage:
   pytest tests/test_spark_analytics.py --cov=src.spark_analytics

Run specific test:
   pytest tests/test_spark_analytics.py::TestSalesAnalytics::test_top_customers_by_revenue_ordering -v

What tests verify:
✅ Spark session initialization
✅ Configuration settings (Kryo, 4GB, AQE)
✅ Parquet file loading
✅ All 5 analytics methods return correct data types
✅ Column names and order
✅ Result ordering (descending by revenue)
✅ Window functions work correctly
✅ Error handling (missing files)
✅ Context manager cleanup
✅ Integration with real Parquet files

Expected Results:
25+ tests
All PASSED (assuming main.py has been run)

Note: If you see FileNotFoundError, run main.py first to generate data.
"""


# ============================================================================
# PROGRAMMATIC USAGE
# ============================================================================

"""
Use in Python code:
   
   from src.spark_analytics import SalesAnalytics
   
   # With context manager (recommended)
   with SalesAnalytics(app_name="MyAnalysis") as analytics:
       orders = analytics.load_parquet("data/raw/orders.parquet")
       products = analytics.load_parquet("data/raw/products.parquet")
       
       # Get top 5 customers
       top_5 = analytics.top_customers_by_revenue(orders, products, n=5)
       top_5.show(5)
       
       # Get category breakdown
       categories = analytics.sales_by_category(orders, products)
       categories.show()
       
       # Get monthly trends
       trends = analytics.monthly_trends(orders, products)
       trends.show()
   
   # Without context manager
   analytics = SalesAnalytics()
   orders = analytics.load_parquet("data/raw/orders.parquet")
   products = analytics.load_parquet("data/raw/products.parquet")
   
   result = analytics.top_customers_by_revenue(orders, products, n=20)
   result.show(20)
   
   analytics.stop()
"""


# ============================================================================
# EXPORT RESULTS
# ============================================================================

"""
Save results to Parquet:
   
   from src.spark_analytics import SalesAnalytics
   
   with SalesAnalytics() as analytics:
       orders = analytics.load_parquet("data/raw/orders.parquet")
       products = analytics.load_parquet("data/raw/products.parquet")
       
       # Analyze
       top_customers = analytics.top_customers_by_revenue(orders, products, n=100)
       
       # Export to Parquet
       top_customers.write.parquet(
           "data/output/top_customers.parquet",
           mode="overwrite"
       )

Convert to Pandas:
   
   # Convert Spark DataFrame to Pandas for further analysis
   pdf = top_customers.toPandas()
   
   # Now use Pandas operations
   pdf.to_csv("output/top_customers.csv", index=False)
   pdf.to_excel("output/top_customers.xlsx", index=False)
   
   # Create visualizations
   import matplotlib.pyplot as plt
   pdf['total_revenue'].plot(kind='bar')
   plt.savefig('output/top_customers.png')
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Issue: ModuleNotFoundError: No module named 'pyspark'
Solution: pip install pyspark==3.5.0

Issue: FileNotFoundError: Parquet file not found
Solution: Run main.py first to generate data
         python main.py

Issue: Java/Scala errors when importing PySpark
Solution: Ensure Java is installed
         java -version
         Or: python -c "import pyspark; pyspark.SparkContext('local')"

Issue: Out of Memory error
Solution: Reduce data or increase executor memory in Spark config
         .config("spark.executor.memory", "8g")  # Increase to 8GB

Issue: Test failures with "real Parquet" tests
Solution: Verify Parquet files exist in data/raw/
         Verify main.py ran successfully first

""""""

Issue: Slow performance
Solution:
1. Check hardware resources (CPU, RAM)
2. Reduce dataset size (filter in load phase)
3. Cache frequently used DataFrames
4. Increase partitions if using cluster

Issue: Column names not matching expected
Solution: Verify Parquet schema matches expectations
         result.printSchema()
"""


# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

"""
Optimization Techniques:

1. Cache DataFrames if reused multiple times
   df.cache()
   
2. Filter early before analytics
   filtered_orders = orders.filter(col("order_date") > "2024-01-01")
   
3. Use explain() to see query plan
   result.explain(extended=True)
   
4. Coalesce small results before writing
   result.coalesce(1).write.parquet("output.parquet")
   
5. Use partition pruning for large datasets
   orders.partitionBy("year").parquet("data/orders_partitioned/")
   
6. Enable column pruning (already enabled)
   Only reads necessary columns from Parquet

7. Use broadcast hints for small tables
   result = orders.join(
       broadcast(products),
       on="product_id"
   )

8. Adjust parallelism based on data
   spark.sql.shuffle.partitions = 200  # for large data
   spark.sql.shuffle.partitions = 4    # for small data (local)
"""


# ============================================================================
# NEXT STEPS
# ============================================================================

"""
After running analytics:

1. Explore the Data
   - Look at top customers
   - Identify best-performing categories
   - Understand revenue trends

2. Extend the Analytics
   - Add customer segmentation (RFM)
   - Add product correlation analysis
   - Add forecasting

3. Create Visualizations
   - Dashboard with Plotly
   - Charts with Matplotlib
   - Export to PowerBI/Tableau

4. Production Deployment
   - Deploy to Spark cluster
   - Set up scheduled jobs
   - Add alerts and monitoring

5. Integration
   - Connect to data warehouse
   - Feed into BI platforms
   - Expose via API
"""


# ============================================================================
# FILE LOCATIONS
# ============================================================================

"""
Key Files:

Source Code:
  src/spark_analytics.py          ← Main SalesAnalytics class
  analytics_demo.py               ← Running example

Documentation:
  SALESANALYTICS_API.md           ← Quick reference
  SALESANALYTICS_GUIDE.md         ← Complete guide
  PHASE_6_SUMMARY.md              ← This phase summary
  
Tests:
  tests/test_spark_analytics.py   ← Unit tests (25+ tests)
  
Data:
  data/raw/customers.parquet      ← Generated data
  data/raw/products.parquet
  data/raw/orders.parquet
  
Output:
  logs/analytics_demo.log         ← Execution logs
  data/output/*.parquet           ← Exported results (if saved)
  
Configuration:
  requirements.txt                ← Dependencies
  src/config.py                   ← Project config
"""


# ============================================================================
# GETTING HELP
# ============================================================================

"""
View help:

In Python:
  from src.spark_analytics import SalesAnalytics
  help(SalesAnalytics)
  help(SalesAnalytics.top_customers_by_revenue)
  
From command line:
  pydoc src.spark_analytics
  
Check documentation:
  - SALESANALYTICS_API.md for quick reference
  - SALESANALYTICS_GUIDE.md for deep dive
  - tests/test_spark_analytics.py for examples

Run with debug logging:
  # In analytics_demo.py, change log level
  logging.basicConfig(level=logging.DEBUG)
  # Now get more detailed logs
"""
