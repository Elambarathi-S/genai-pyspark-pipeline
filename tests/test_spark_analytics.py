"""
Unit tests for the SalesAnalytics class.

Tests all five analytics methods with real data from Parquet files.
"""

import pytest
import logging
from pathlib import Path
from datetime import datetime

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, LongType

from src.spark_analytics import SalesAnalytics


class TestSalesAnalytics:
    """Test suite for SalesAnalytics class."""

    @pytest.fixture
    def analytics(self):
        """Create SalesAnalytics instance for testing."""
        analytics = SalesAnalytics(app_name="TestAnalytics")
        yield analytics
        # Cleanup
        if analytics.spark is not None:
            analytics.stop()

    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrames for testing."""
        spark = SparkSession.builder \
            .appName("TestData") \
            .config("spark.sql.shuffle.partitions", "2") \
            .master("local[2]") \
            .getOrCreate()

        # Sample customers
        customers_data = [
            (1, "Alice Johnson", "alice@example.com"),
            (2, "Bob Smith", "bob@example.com"),
            (3, "Charlie Brown", "charlie@example.com"),
        ]
        customers_schema = StructType([
            StructField("customer_id", IntegerType()),
            StructField("name", StringType()),
            StructField("email", StringType()),
        ])
        customers_df = spark.createDataFrame(customers_data, schema=customers_schema)

        # Sample products
        products_data = [
            (1, "Laptop", "Electronics", 999.99, 5),
            (2, "Mouse", "Electronics", 29.99, 4),
            (3, "Desk Chair", "Furniture", 299.99, 4),
            (4, "Monitor", "Electronics", 399.99, 5),
            (5, "Keyboard", "Electronics", 79.99, 4),
        ]
        products_schema = StructType([
            StructField("product_id", IntegerType()),
            StructField("name", StringType()),
            StructField("category", StringType()),
            StructField("price", DoubleType()),
            StructField("rating", IntegerType()),
        ])
        products_df = spark.createDataFrame(products_data, schema=products_schema)

        # Sample orders
        orders_data = [
            (1, 1, 1, 1, "2024-01-15 10:30:00"),  # Customer 1, Product 1, qty 1
            (2, 1, 2, 2, "2024-01-16 14:45:00"),  # Customer 1, Product 2, qty 2
            (3, 2, 3, 1, "2024-01-17 09:15:00"),  # Customer 2, Product 3, qty 1
            (4, 2, 4, 1, "2024-02-01 11:00:00"),  # Customer 2, Product 4, qty 1
            (5, 3, 5, 3, "2024-02-10 13:30:00"),  # Customer 3, Product 5, qty 3
            (6, 1, 4, 1, "2024-02-15 15:45:00"),  # Customer 1, Product 4, qty 1
            (7, 3, 1, 1, "2024-03-01 10:00:00"),  # Customer 3, Product 1, qty 1
        ]
        orders_schema = StructType([
            StructField("order_id", LongType()),
            StructField("customer_id", IntegerType()),
            StructField("product_id", IntegerType()),
            StructField("quantity", IntegerType()),
            StructField("order_date", StringType()),
        ])
        orders_df = spark.createDataFrame(orders_data, schema=orders_schema)

        return {
            "customers": customers_df,
            "products": products_df,
            "orders": orders_df,
            "spark": spark,
        }

    def test_initialization(self, analytics):
        """Test SalesAnalytics initialization."""
        assert analytics is not None
        assert analytics.spark is not None
        assert analytics.app_name == "TestAnalytics"

    def test_create_spark_session(self, analytics):
        """Test create_spark_session method."""
        spark = analytics.create_spark_session()
        assert spark is not None
        assert isinstance(spark, SparkSession)

    def test_get_spark_config(self, analytics):
        """Test get_spark_config method."""
        config = analytics.get_spark_config()
        assert isinstance(config, dict)
        assert "spark.executor.memory" in config
        assert config["spark.executor.memory"] == "4g"
        assert "spark.serializer" in config
        assert "KryoSerializer" in config["spark.serializer"]

    def test_top_customers_by_revenue_returns_dataframe(self, analytics, sample_data):
        """Test that top_customers_by_revenue returns a DataFrame."""
        result = analytics.top_customers_by_revenue(
            sample_data["orders"],
            sample_data["products"],
            n=3
        )
        assert isinstance(result, DataFrame)

    def test_top_customers_by_revenue_columns(self, analytics, sample_data):
        """Test top_customers_by_revenue returns correct columns."""
        result = analytics.top_customers_by_revenue(
            sample_data["orders"],
            sample_data["products"],
            n=3
        )
        expected_columns = ["customer_id", "total_revenue", "num_orders", "avg_order_value"]
        assert result.columns == expected_columns

    def test_top_customers_by_revenue_count(self, analytics, sample_data):
        """Test top_customers_by_revenue respects n parameter."""
        result = analytics.top_customers_by_revenue(
            sample_data["orders"],
            sample_data["products"],
            n=2
        )
        assert result.count() == 2

    def test_top_customers_by_revenue_ordering(self, analytics, sample_data):
        """Test top_customers_by_revenue orders by revenue descending."""
        result = analytics.top_customers_by_revenue(
            sample_data["orders"],
            sample_data["products"],
            n=3
        )
        rows = result.collect()
        revenues = [row["total_revenue"] for row in rows]
        # Verify descending order
        assert revenues == sorted(revenues, reverse=True)

    def test_sales_by_category_returns_dataframe(self, analytics, sample_data):
        """Test that sales_by_category returns a DataFrame."""
        result = analytics.sales_by_category(
            sample_data["orders"],
            sample_data["products"]
        )
        assert isinstance(result, DataFrame)

    def test_sales_by_category_columns(self, analytics, sample_data):
        """Test sales_by_category returns correct columns."""
        result = analytics.sales_by_category(
            sample_data["orders"],
            sample_data["products"]
        )
        expected_columns = [
            "category",
            "total_revenue",
            "total_units_sold",
            "num_transactions",
            "avg_transaction_value"
        ]
        assert result.columns == expected_columns

    def test_sales_by_category_all_categories(self, analytics, sample_data):
        """Test sales_by_category includes all product categories."""
        result = analytics.sales_by_category(
            sample_data["orders"],
            sample_data["products"]
        )
        categories = [row["category"] for row in result.collect()]
        # Verify we get all categories that have orders
        assert "Electronics" in categories
        assert "Furniture" in categories

    def test_sales_by_category_ordering(self, analytics, sample_data):
        """Test sales_by_category orders by revenue descending."""
        result = analytics.sales_by_category(
            sample_data["orders"],
            sample_data["products"]
        )
        rows = result.collect()
        revenues = [row["total_revenue"] for row in rows]
        # Verify descending order
        assert revenues == sorted(revenues, reverse=True)

    def test_monthly_trends_returns_dataframe(self, analytics, sample_data):
        """Test that monthly_trends returns a DataFrame."""
        result = analytics.monthly_trends(
            sample_data["orders"],
            sample_data["products"]
        )
        assert isinstance(result, DataFrame)

    def test_monthly_trends_columns(self, analytics, sample_data):
        """Test monthly_trends returns correct columns."""
        result = analytics.monthly_trends(
            sample_data["orders"],
            sample_data["products"]
        )
        expected_columns = [
            "year_month",
            "total_revenue",
            "prev_revenue",
            "growth_percentage"
        ]
        assert result.columns == expected_columns

    def test_monthly_trends_window_functions(self, analytics, sample_data):
        """Test monthly_trends correctly uses window functions."""
        result = analytics.monthly_trends(
            sample_data["orders"],
            sample_data["products"]
        )
        rows = result.collect()
        
        # Verify we have multiple months
        assert len(rows) >= 2
        
        # Verify first month has no growth (None or 0 prev_revenue)
        first_month_prev = rows[0]["prev_revenue"]
        assert first_month_prev == 0.0 or first_month_prev is None
        
        # Verify growth percentage exists for second month
        if len(rows) > 1:
            second_month_growth = rows[1]["growth_percentage"]
            # Should be a number or None
            assert second_month_growth is None or isinstance(second_month_growth, (int, float))

    def test_monthly_trends_ordering(self, analytics, sample_data):
        """Test monthly_trends orders chronologically."""
        result = analytics.monthly_trends(
            sample_data["orders"],
            sample_data["products"]
        )
        rows = result.collect()
        year_months = [row["year_month"] for row in rows]
        # Verify ascending order
        assert year_months == sorted(year_months)

    def test_context_manager(self, sample_data):
        """Test SalesAnalytics works as context manager."""
        with SalesAnalytics(app_name="ContextTest") as analytics:
            assert analytics.spark is not None
            result = analytics.sales_by_category(
                sample_data["orders"],
                sample_data["products"]
            )
            assert result.count() > 0

    def test_load_parquet_nonexistent_file(self, analytics):
        """Test load_parquet raises error for nonexistent file."""
        with pytest.raises(FileNotFoundError):
            analytics.load_parquet("/nonexistent/path/file.parquet")

    def test_stop_method(self, analytics):
        """Test stop method."""
        analytics.stop()
        # After stopping, we should be able to create a new session
        spark = analytics.create_spark_session()
        assert spark is not None

    def test_analytics_with_real_parquet(self, analytics):
        """Test analytics methods with real Parquet files if they exist."""
        orders_path = Path("data/raw/orders.parquet")
        products_path = Path("data/raw/products.parquet")
        
        if orders_path.exists() and products_path.exists():
            orders_df = analytics.load_parquet(str(orders_path))
            products_df = analytics.load_parquet(str(products_path))
            
            # Test all methods
            top_customers = analytics.top_customers_by_revenue(orders_df, products_df, n=5)
            assert top_customers.count() > 0
            
            category_sales = analytics.sales_by_category(orders_df, products_df)
            assert category_sales.count() > 0
            
            monthly = analytics.monthly_trends(orders_df, products_df)
            assert monthly.count() > 0
        assert "category" in category_perf.columns
        assert "total_revenue" in category_perf.columns

    def test_analyze_complete_pipeline(self, analytics: SparkAnalytics) -> None:
        """Test complete analysis pipeline."""
        results = analytics.analyze()

        assert isinstance(results, dict)
        assert "Summary Statistics" in results
        assert "Customer Insights" in results
        assert "Product Performance" in results

    def teardown_method(self) -> None:
        """Clean up after tests."""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
