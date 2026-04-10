"""
PySpark analytics module for the e-commerce data pipeline.

This module provides the SalesAnalytics class for analyzing e-commerce sales data
using PySpark for distributed processing with advanced analytics capabilities.
"""

import logging
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    sum as spark_sum,
    count,
    avg,
    max as spark_max,
    min as spark_min,
    desc,
    asc,
    col,
    when,
    year,
    month,
    to_date,
    date_trunc,
    lag,
    row_number,
    round as spark_round,
    coalesce,
)
from pyspark.sql.window import Window
import pandas as pd


class SalesAnalytics:
    """
    PySpark-based analytics for e-commerce sales data.

    This class provides methods for analyzing customer purchases, product performance,
    and sales trends using PySpark's distributed computing capabilities.
    """

    def __init__(self, app_name: str = "SalesAnalytics") -> None:
        """
        Initialize SalesAnalytics with a configured Spark session.

        Args:
            app_name: Name of the Spark application (default: "SalesAnalytics")
        """
        self.logger = logging.getLogger(__name__)
        self.app_name = app_name
        self.spark: Optional[SparkSession] = None
        self._initialize_spark_session()

    def _initialize_spark_session(self) -> None:
        """
        Create and configure a Spark session with optimized settings.

        Configuration includes:
        - 4GB executor memory
        - Adaptive Query Execution (AQE)
        - Kryo serialization for performance
        - Local mode with 4 partitions
        """
        try:
            self.spark = (
                SparkSession.builder
                .appName(self.app_name)
                # Memory configuration
                .config("spark.executor.memory", "4g")
                .config("spark.driver.memory", "4g")
                # Adaptive Query Execution
                .config("spark.sql.adaptive.enabled", "true")
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
                .config("spark.sql.adaptive.skewJoin.enabled", "true")
                # Serialization
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
                .config("spark.kryoserializer.buffer.max", "512m")
                # Query optimization
                .config("spark.sql.shuffle.partitions", "4")
                .config("spark.sql.broadcastTimeout", "600")
                # Performance tuning
                .config("spark.sql.statistics.histogram.enabled", "true")
                .config("spark.sql.statistics.histogram.num.bins", "100")
                # Local mode settings
                .master("local[4]")
                .getOrCreate()
            )

            # Set log level to WARNING to reduce output
            self.spark.sparkContext.setLogLevel("WARN")
            self.logger.info(f"✓ Spark session '{self.app_name}' initialized successfully")
            self.logger.info(f"  Spark version: {self.spark.version}")
            self.logger.info(f"  Master: {self.spark.sparkContext.master}")

        except Exception as e:
            self.logger.error(f"Failed to initialize Spark session: {e}")
            raise

    def create_spark_session(self) -> SparkSession:
        """
        Get or create the Spark session.

        Returns:
            Configured SparkSession instance
        """
        if self.spark is None:
            self._initialize_spark_session()
        return self.spark

    def load_parquet(self, path: str) -> DataFrame:
        """
        Load a Parquet file into a Spark DataFrame.

        Args:
            path: Path to the Parquet file or directory

        Returns:
            Spark DataFrame containing the loaded data

        Raises:
            FileNotFoundError: If the path does not exist
            Exception: If there's an error reading the Parquet file
        """
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                raise FileNotFoundError(f"Parquet file not found: {path}")

            self.logger.info(f"Loading Parquet file: {path}")
            df = self.spark.read.parquet(path)
            row_count = df.count()
            self.logger.info(f"✓ Loaded {row_count:,} rows from {path}")
            return df

        except FileNotFoundError as e:
            self.logger.error(str(e))
            raise
        except Exception as e:
            self.logger.error(f"Error loading Parquet file: {e}")
            raise

    def top_customers_by_revenue(
        self,
        orders_df: DataFrame,
        products_df: DataFrame,
        n: int = 10,
    ) -> DataFrame:
        """
        Find top N customers by total revenue spent.

        Joins orders with products, calculates total revenue per customer,
        and returns the top N customers.

        Args:
            orders_df: DataFrame with columns: order_id, customer_id, product_id, quantity, order_date
            products_df: DataFrame with columns: product_id, name, category, price, rating
            n: Number of top customers to return (default: 10)

        Returns:
            DataFrame with columns: customer_id, total_revenue, num_orders, avg_order_value
            Sorted by total_revenue in descending order
        """
        try:
            self.logger.info(f"Calculating top {n} customers by revenue...")

            # Calculate line total with revenue
            orders_with_revenue = orders_df.join(
                products_df.select("product_id", "price"),
                on="product_id",
                how="inner"
            ).withColumn(
                "revenue",
                col("quantity") * col("price")
            )

            # Group by customer and calculate metrics
            customer_revenue = orders_with_revenue.groupby("customer_id").agg(
                spark_sum("revenue").alias("total_revenue"),
                count("order_id").alias("num_orders"),
                avg("revenue").alias("avg_order_value"),
            ).orderBy(desc("total_revenue")).limit(n)

            result = customer_revenue.select(
                "customer_id",
                spark_round("total_revenue", 2).alias("total_revenue"),
                "num_orders",
                spark_round("avg_order_value", 2).alias("avg_order_value"),
            )

            self.logger.info(f"✓ Retrieved top {n} customers")
            return result

        except Exception as e:
            self.logger.error(f"Error calculating top customers: {e}")
            raise

    def sales_by_category(
        self,
        orders_df: DataFrame,
        products_df: DataFrame,
    ) -> DataFrame:
        """
        Calculate sales metrics grouped by product category.

        Aggregates revenue and units sold for each product category.

        Args:
            orders_df: DataFrame with columns: order_id, product_id, quantity, order_date
            products_df: DataFrame with columns: product_id, name, category, price

        Returns:
            DataFrame with columns: category, total_revenue, total_units_sold, num_transactions, avg_transaction_value
            Sorted by total_revenue in descending order
        """
        try:
            self.logger.info("Calculating sales by category...")

            # Join orders with products to get categories
            orders_with_category = orders_df.join(
                products_df.select("product_id", "category", "price"),
                on="product_id",
                how="inner"
            ).withColumn(
                "revenue",
                col("quantity") * col("price")
            )

            # Group by category and aggregate
            category_sales = orders_with_category.groupby("category").agg(
                spark_sum("revenue").alias("total_revenue"),
                spark_sum("quantity").alias("total_units_sold"),
                count("order_id").alias("num_transactions"),
                avg("revenue").alias("avg_transaction_value"),
            ).orderBy(desc("total_revenue"))

            result = category_sales.select(
                "category",
                spark_round("total_revenue", 2).alias("total_revenue"),
                "total_units_sold",
                "num_transactions",
                spark_round("avg_transaction_value", 2).alias("avg_transaction_value"),
            )

            self.logger.info("✓ Calculated sales by category")
            return result

        except Exception as e:
            self.logger.error(f"Error calculating sales by category: {e}")
            raise

    def monthly_trends(
        self,
        orders_df: DataFrame,
        products_df: DataFrame,
    ) -> DataFrame:
        """
        Calculate month-over-month revenue growth trends.

        Uses Window functions to calculate growth percentages between consecutive months.

        Args:
            orders_df: DataFrame with columns: order_id, product_id, quantity, order_date
            products_df: DataFrame with columns: product_id, price

        Returns:
            DataFrame with columns: year_month, total_revenue, prev_revenue, growth_percentage
            Sorted by year_month in ascending order
        """
        try:
            self.logger.info("Calculating monthly revenue trends...")

            # Convert order_date to timestamp and extract year-month
            orders_with_month = orders_df.join(
                products_df.select("product_id", "price"),
                on="product_id",
                how="inner"
            ).withColumn(
                "revenue",
                col("quantity") * col("price")
            ).withColumn(
                "order_date_ts",
                to_date(col("order_date"), "yyyy-MM-dd")
            ).withColumn(
                "year_month",
                date_trunc("month", col("order_date_ts"))
            )

            # Monthly revenue aggregation
            monthly_revenue = orders_with_month.groupby("year_month").agg(
                spark_sum("revenue").alias("total_revenue")
            ).orderBy("year_month")

            # Apply Window function to calculate growth
            window_spec = Window.orderBy("year_month")
            monthly_with_lag = monthly_revenue.withColumn(
                "prev_revenue",
                lag("total_revenue").over(window_spec)
            ).withColumn(
                "growth_percentage",
                when(
                    col("prev_revenue").isNull(),
                    None
                ).otherwise(
                    spark_round(
                        ((col("total_revenue") - col("prev_revenue")) / col("prev_revenue")) * 100,
                        2
                    )
                )
            )

            result = monthly_with_lag.select(
                col("year_month").cast("string").alias("year_month"),
                spark_round("total_revenue", 2).alias("total_revenue"),
                spark_round(coalesce("prev_revenue", 0), 2).alias("prev_revenue"),
                "growth_percentage",
            )

            self.logger.info("✓ Calculated monthly revenue trends")
            return result

        except Exception as e:
            self.logger.error(f"Error calculating monthly trends: {e}")
            raise

    def get_spark_config(self) -> dict:
        """
        Get current Spark configuration settings.

        Returns:
            Dictionary of Spark configuration key-value pairs
        """
        if self.spark is None:
            return {}

        config_dict = {}
        for key in self.spark.sparkContext.getConf().getAll():
            config_dict[key[0]] = key[1]
        return config_dict

    def stop(self) -> None:
        """Stop the Spark session."""
        if self.spark is not None:
            self.spark.stop()
            self.logger.info("✓ Spark session stopped")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# Backward compatibility: keep SparkAnalytics as an alias
SparkAnalytics = SalesAnalytics
