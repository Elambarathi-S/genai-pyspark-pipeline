"""
RUNNING ANALYTICS - Setup & Usage Guide

This document explains both analytics options and how to set them up.
"""

# ============================================================================
# OPTION 1: PANDAS ANALYTICS (No Java Required) ⭐ RECOMMENDED FOR QUICK TEST
# ============================================================================

PANDAS_OPTION = """
QUICK START - Run immediately without Java:

    python run_analytics_pandas.py

What it does:
✅ Loads Parquet files (100K customers, 10K products, 1M orders)
✅ Runs all 3 analytics methods using Pandas
✅ Displays results
✅ Shows execution timing (typically 1-2 seconds)

Suitable for:
- Quick testing and validation
- Development and debugging
- Local analysis on smaller datasets

Results Example:
────────────────
📊 Data loaded successfully
   Customers: 100,000 rows
   Products: 10,000 rows
   Orders: 1,000,000 rows

Top 10 Customers by Revenue:
   customer_id  |  total_revenue  |  num_orders  |  avg_order_value
   1            |  $539,386,454   |  726,453     |  $742.49
   2            |  $91,597,876    |  123,131     |  $743.91
   ...

Sales by Category:
   category    |  total_revenue  |  units_sold  |  transactions
   Electronics |  $301,680,974   |  1,098,801   |  199,837
   Home        |  $173,924,742   |  1,080,494   |  196,380
   ...

Monthly Trends:
   year_month  |  total_revenue  |  growth_percentage
   2025-04     |  $44,403,981    |  -
   2025-05     |  $63,018,542    |  +41.92%
   2025-06     |  $60,796,395    |  -3.53%
   ...

Execution Time: ~1.2 seconds total
────────────────
"""


# ============================================================================
# OPTION 2: PYSPARK ANALYTICS (Distributed Computing) ⭐ RECOMMENDED FOR PRODUCTION
# ============================================================================

PYSPARK_OPTION = """
FULL-FEATURED - For production and larger datasets (requires Java):

    python run_analytics.py

What it does:
✅ Uses PySpark for distributed computing
✅ Optimized for large-scale data (100GB+)
✅ Adaptive Query Execution (AQE)
✅ Kryo serialization for performance
✅ Window functions for advanced analytics
✅ Can scale to Spark clusters

Suitable for:
- Production deployments
- Large datasets (> 1GB)
- Distributed/cluster computing
- Advanced analytics requirements

Prerequisites:
❌ Java Development Kit (JDK) 8 or later
❌ Set JAVA_HOME environment variable
"""


# ============================================================================
# INSTALLING JAVA (For PySpark Option)
# ============================================================================

JAVA_SETUP = """
STEP 1: INSTALL JDK

Download JDK 8 or later from:
  https://www.oracle.com/java/technologies/downloads/

Or using package manager:
  Windows (Chocolatey):
    choco install openjdk
  
  OR download installer from above link

STEP 2: SET JAVA_HOME environment variable

Windows (PowerShell):
  $env:JAVA_HOME = "C:\\Program Files\\Java\\jdk-11.0.13"
  
  OR set permanently via System Settings:
  1. Open System Properties
  2. Click "Environment Variables"
  3. Click "New" (under System variables)
  4. Variable name: JAVA_HOME
  5. Variable value: C:\\Program Files\\Java\\jdk-11.0.13
     (adjust path to your JDK installation)
  6. Click OK and restart PowerShell

STEP 3: VERIFY INSTALLATION

  java -version
  
Expected output:
  openjdk version "11.0.13" 2021-10-19
  OpenJDK Runtime Environment (build 11.0.13+8-post-Ubuntu-0ubuntu120.04)
  OpenJDK 64-Bit Server VM (build 11.0.13+8-post-Ubuntu-0ubuntu120.04, mixed mode)

STEP 4: RUN PYSPARK ANALYTICS

  python run_analytics.py
"""


# ============================================================================
# COMPARISON
# ============================================================================

COMPARISON = """
┌─────────────────────┬──────────────────┬──────────────────┐
│ Feature             │ Pandas Version   │ PySpark Version  │
├─────────────────────┼──────────────────┼──────────────────┤
│ Setup Required      │ None (quick!)    │ Java + JAVA_HOME │
│ Speed (1M orders)   │ ~1 second        │ ~20 seconds      │
│ Max Dataset Size    │ Machine RAM (~64GB) │ Unlimited (clusters) │
│ Distributed         │ No (single node) │ Yes (scalable)   │
│ Window Functions    │ Basic            │ Advanced         │
│ Best Use Case       │ Testing/Dev      │ Production/BigData│
│ Production Ready    │ ⭐               │ ⭐⭐⭐          │
└─────────────────────┴──────────────────┴──────────────────┘

TL;DR:
- Need quick demo? → python run_analytics_pandas.py
- Need production setup? → Install Java, then python run_analytics.py
"""


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

EXAMPLES = """
EXAMPLE 1: Quick Test (1 minute)
  python run_analytics_pandas.py
  # Results displayed, no setup needed

EXAMPLE 2: PySpark with Java (first time, 5 minutes)
  1. Download and install JDK
  2. Set JAVA_HOME environment variable
  3. python run_analytics.py
  # Full PySpark output with timing

EXAMPLE 3: Programmatic Usage
  from src.spark_analytics import SalesAnalytics
  
  with SalesAnalytics() as analytics:
      orders = analytics.load_parquet("data/raw/orders.parquet")
      products = analytics.load_parquet("data/raw/products.parquet")
      
      top_customers = analytics.top_customers_by_revenue(orders, products, n=10)
      top_customers.show()

EXAMPLE 4: Using Pandas Programmatically
  import pandas as pd
  
  customers = pd.read_parquet("data/raw/customers.parquet")
  products = pd.read_parquet("data/raw/products.parquet")
  orders = pd.read_parquet("data/raw/orders.parquet")
  
  # Perform pandas analytics...
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

TROUBLESHOOTING = """
Issue: "ModuleNotFoundError: No module named 'pyspark'"
Solution: Already installed! Try Option 1 (Pandas) first while testing.

Issue: "Java not found" / "JAVA_HOME not set"
Solution: Follow JAVA_SETUP instructions above to install JDK and set JAVA_HOME

Issue: "FileNotFoundError: Parquet file not found"
Solution: Run main.py first to generate data:
         python main.py

Issue: "ModuleNotFoundError: No module named 'pandas'"
Solution: pip install pandas (pandas already in requirements.txt)

Issue: Script runs but shows incorrect data
Solution: Verify Parquet files were generated correctly:
         python main.py
         # Then try analytics again

Issue: Very slow performance with PySpark
Solution: PySpark startup is slow on first run (~15 seconds).
         Subsequent runs are faster. This is expected.
         For single-node single-run, Pandas is faster.
"""


# ============================================================================
# QUICK START CHECKLIST
# ============================================================================

CHECKLIST = """
✅ QUICK START CHECKLIST

For Pandas Analytics (works now):
  ☐ Data generated (main.py run successfully)
  ☐ Run: python run_analytics_pandas.py
  ☐ View results in console
  
For PySpark Analytics (if you want distributed computing):
  ☐ Data generated (main.py run successfully)
  ☐ Install JDK 8+
  ☐ Set JAVA_HOME environment variable
  ☐ Run: python run_analytics.py
  ☐ View PySpark results in console
"""


# ============================================================================
# FILE LOCATIONS
# ============================================================================

FILES = """
Key Files:

Scripts:
  run_analytics_pandas.py  ← Use this if Java is not installed
  run_analytics.py         ← Use this if Java is installed
  
Source:
  src/spark_analytics.py   ← SalesAnalytics class (uses PySpark)
  
Data (generated by main.py):
  data/raw/customers.parquet
  data/raw/products.parquet
  data/raw/orders.parquet
"""


# ============================================================================
# PRINTING
# ============================================================================

if __name__ == "__main__":
    print(PANDAS_OPTION)
    print("\n" + "="*80 + "\n")
    print(PYSPARK_OPTION)
    print("\n" + "="*80 + "\n")
    print(JAVA_SETUP)
    print("\n" + "="*80 + "\n")
    print(COMPARISON)
    print("\n" + "="*80 + "\n")
    print(EXAMPLES)
    print("\n" + "="*80 + "\n")
    print(TROUBLESHOOTING)
    print("\n" + "="*80 + "\n")
    print(CHECKLIST)
    print("\n" + "="*80 + "\n")
    print(FILES)
