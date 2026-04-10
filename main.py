"""
Main data generation script for e-commerce synthetic data pipeline.

This script demonstrates:
1. Generating synthetic data with SyntheticDataGenerator
2. Saving data as Parquet files (more efficient than CSV)
3. Reporting generation time and file sizes
4. Proper error handling and logging
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import time

from src.config import Config
from src.data_generator import SyntheticDataGenerator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (B, KB, MB, GB)
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def save_as_parquet(df, filepath: Path) -> int:
    """
    Save DataFrame as Parquet file.

    Args:
        df: Pandas DataFrame to save
        filepath: Path to save the Parquet file

    Returns:
        File size in bytes
    """
    try:
        df.to_parquet(filepath, index=False, compression="snappy")
        file_size = filepath.stat().st_size
        return file_size
    except ImportError:
        logger.warning("PyArrow not available, falling back to CSV format")
        csv_path = filepath.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        file_size = csv_path.stat().st_size
        return file_size
    except Exception as e:
        logger.warning(f"Error saving Parquet: {e}. Falling back to CSV format")
        csv_path = filepath.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        file_size = csv_path.stat().st_size
        return file_size


def main() -> None:
    """Run the complete data generation pipeline."""
    try:
        print("=" * 80)
        print("E-COMMERCE SYNTHETIC DATA GENERATION PIPELINE")
        print("=" * 80)

        # Initialize configuration
        logger.info("Initializing configuration...")
        config = Config()
        config.log_config()

        # Initialize data generator
        logger.info("Initializing SyntheticDataGenerator...")
        generator = SyntheticDataGenerator(
            config=config,
            num_customers=100000,
            num_products=10000,
            num_orders=1000000,
        )

        # Start timing
        start_time = time.time()
        start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Generation started at: {start_datetime}")

        print("\n" + "=" * 80)
        print("STEP 1: GENERATING DATA")
        print("=" * 80)

        # Generate all data
        data = generator.generate_and_save_all()

        print("\n" + "=" * 80)
        print("STEP 2: SAVING TO PARQUET FILE FORMAT")
        print("=" * 80)

        # Save as Parquet files (more efficient than CSV)
        logger.info("Saving data to Parquet files...")

        # Save customers
        logger.info("Saving customers to Parquet...")
        customers_parquet_path = config.raw_data_dir / "customers.parquet"
        customers_size = save_as_parquet(data["customers"], customers_parquet_path)
        logger.info(f"✓ Saved customers ({len(data['customers']):,} rows)")

        # Save products
        logger.info("Saving products to Parquet...")
        products_parquet_path = config.raw_data_dir / "products.parquet"
        products_size = save_as_parquet(data["products"], products_parquet_path)
        logger.info(f"✓ Saved products ({len(data['products']):,} rows)")

        # Save orders
        logger.info("Saving orders to Parquet...")
        orders_parquet_path = config.raw_data_dir / "orders.parquet"
        orders_size = save_as_parquet(data["orders"], orders_parquet_path)
        logger.info(f"✓ Saved orders ({len(data['orders']):,} rows)")

        # Calculate elapsed time
        end_time = time.time()
        elapsed_time = end_time - start_time
        end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Print summary report
        print("\n" + "=" * 80)
        print("GENERATION SUMMARY REPORT")
        print("=" * 80)

        print(f"\n✓ Data Generation Completed!")
        print(f"\nTiming Information:")
        print(f"  Start time: {start_datetime}")
        print(f"  End time: {end_datetime}")
        print(f"  Total time: {elapsed_time:.2f} seconds ({elapsed_time / 60:.2f} minutes)")

        print(f"\nData Summary:")
        print(f"  Customers: {len(data['customers']):,} rows")
        print(f"  Products: {len(data['products']):,} rows")
        print(f"  Orders: {len(data['orders']):,} rows")
        print(f"  Total records: {len(data['customers']) + len(data['products']) + len(data['orders']):,}")

        print(f"\nFile Sizes (Parquet Format):")
        print(f"  Customers: {format_file_size(customers_size)}")
        print(f"  Products: {format_file_size(products_size)}")
        print(f"  Orders: {format_file_size(orders_size)}")
        print(f"  Total: {format_file_size(customers_size + products_size + orders_size)}")

        print(f"\nFile Locations:")
        print(f"  Customers: {customers_parquet_path}")
        print(f"  Products: {products_parquet_path}")
        print(f"  Orders: {orders_parquet_path}")

        # Display Pareto distribution
        print("\n" + "=" * 80)
        print("PARETO DISTRIBUTION ANALYSIS (80/20 Rule)")
        print("=" * 80)

        orders_per_customer = data["orders"].groupby("customer_id").size()
        top_20_percent = int(len(data["customers"]) * 0.2)
        top_20_orders = orders_per_customer.nlargest(top_20_percent).sum()
        total_orders = len(data["orders"])
        pareto_ratio = (top_20_orders / total_orders) * 100

        print(f"\nPareto Distribution Statistics:")
        print(f"  Total customers: {len(data['customers']):,}")
        print(f"  Top 20% (customers): {top_20_percent:,}")
        print(f"  Total orders: {total_orders:,}")
        print(f"  Orders by top 20%: {top_20_orders:,}")
        print(f"  Pareto ratio: {pareto_ratio:.1f}%")
        print(f"  Expected ratio: ~80%")

        # Display data quality checks
        print("\n" + "=" * 80)
        print("DATA QUALITY VERIFICATION")
        print("=" * 80)

        quality_checks = {
            "✓ No duplicate customer IDs": data["customers"]["customer_id"].is_unique,
            "✓ No duplicate product IDs": data["products"]["product_id"].is_unique,
            "✓ No duplicate order IDs": data["orders"]["order_id"].is_unique,
            "✓ Valid customer ages (18-80)": (
                (data["customers"]["age"] >= 18).all()
                and (data["customers"]["age"] <= 80).all()
            ),
            "✓ Valid product ratings (1-5)": (
                (data["products"]["rating"] >= 1).all()
                and (data["products"]["rating"] <= 5).all()
            ),
            "✓ Valid order quantities (1-10)": (
                (data["orders"]["quantity"] >= 1).all()
                and (data["orders"]["quantity"] <= 10).all()
            ),
            "✓ All orders reference valid customers": data["orders"]["customer_id"].isin(
                data["customers"]["customer_id"]
            ).all(),
            "✓ All orders reference valid products": data["orders"]["product_id"].isin(
                data["products"]["product_id"]
            ).all(),
        }

        for check_name, check_result in quality_checks.items():
            status = "PASS" if check_result else "FAIL"
            symbol = "✓" if check_result else "✗"
            print(f"  {symbol} {check_name}: {status}")

        print("\n" + "=" * 80)
        print("✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        print("=" * 80)

        logger.info("Main pipeline execution completed successfully!")

    except Exception as e:
        logger.error(f"Error during pipeline execution: {e}", exc_info=True)
        print("\n" + "=" * 80)
        print("❌ ERROR DURING EXECUTION")
        print("=" * 80)
        print(f"\nError: {e}")
        print(f"\nPlease check the logs above for more details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
