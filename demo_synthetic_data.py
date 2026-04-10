"""
Demo script showcasing the SyntheticDataGenerator capabilities.

This script demonstrates:
- Generating large-scale synthetic data (100K customers, 10K products, 1M orders)
- Pareto distribution (80/20 rule)
- Custom configurations
- Data quality checks
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
import pandas as pd
from src.config import Config
from src.data_generator import SyntheticDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def demo_small_scale() -> None:
    """Demo with smaller dataset for quick testing."""
    print("\n" + "=" * 70)
    print("DEMO 1: SMALL-SCALE DATA GENERATION (Quick Test)")
    print("=" * 70)

    config = Config()
    generator = SyntheticDataGenerator(
        config=config,
        num_customers=1000,
        num_products=100,
        num_orders=10000,
    )

    data = generator.generate_and_save_all()
    generator.get_data_summary(
        data["customers"], data["products"], data["orders"]
    )


def demo_medium_scale() -> None:
    """Demo with medium dataset."""
    print("\n" + "=" * 70)
    print("DEMO 2: MEDIUM-SCALE DATA GENERATION")
    print("=" * 70)

    config = Config()
    generator = SyntheticDataGenerator(
        config=config,
        num_customers=10000,
        num_products=1000,
        num_orders=100000,
    )

    data = generator.generate_and_save_all()
    generator.get_data_summary(
        data["customers"], data["products"], data["orders"]
    )


def demo_large_scale() -> None:
    """Demo with large dataset (default: 100K customers, 10K products, 1M orders)."""
    print("\n" + "=" * 70)
    print("DEMO 3: LARGE-SCALE DATA GENERATION (Default: 100K, 10K, 1M)")
    print("=" * 70)

    config = Config()
    generator = SyntheticDataGenerator(
        config=config,
        num_customers=100000,
        num_products=10000,
        num_orders=1000000,
    )

    data = generator.generate_and_save_all()
    generator.get_data_summary(
        data["customers"], data["products"], data["orders"]
    )


def demo_pareto_analysis(df_orders: pd.DataFrame, num_customers: int) -> None:
    """Analyze and display Pareto distribution statistics."""
    print("\n" + "=" * 70)
    print("PARETO DISTRIBUTION ANALYSIS (80/20 Rule)")
    print("=" * 70)

    orders_per_customer = df_orders.groupby("customer_id").size()

    # Calculate statistics
    top_20_percent_count = int(num_customers * 0.2)
    top_20_orders = orders_per_customer.nlargest(top_20_percent_count).sum()
    total_orders = len(df_orders)
    pareto_ratio = (top_20_orders / total_orders) * 100

    print(f"\nTotal customers: {num_customers:,}")
    print(f"Top 20% of customers: {top_20_percent_count:,}")
    print(f"Total orders: {total_orders:,}")
    print(f"Orders by top 20%: {top_20_orders:,}")
    print(f"Pareto ratio: {pareto_ratio:.1f}%")
    print(f"\nExpected Pareto ratio: ~80%")
    print(f"Achieved ratio: {pareto_ratio:.1f}%")
    print(f"Deviation: {abs(80 - pareto_ratio):.1f}%")

    # Order distribution stats
    print(f"\nOrder distribution per customer:")
    print(f"  Mean: {orders_per_customer.mean():.2f}")
    print(f"  Std: {orders_per_customer.std():.2f}")
    print(f"  Min: {orders_per_customer.min()}")
    print(f"  Max: {orders_per_customer.max()}")
    print(f"  Median: {orders_per_customer.median():.0f}")


def demo_data_quality_checks(data: dict) -> None:
    """Perform data quality checks."""
    print("\n" + "=" * 70)
    print("DATA QUALITY CHECKS")
    print("=" * 70)

    df_customers = data["customers"]
    df_products = data["products"]
    df_orders = data["orders"]

    print("\nCustomer Data Quality:")
    print(f"  ✓ No duplicate customer IDs: {df_customers['customer_id'].is_unique}")
    print(f"  ✓ No null names: {df_customers['name'].notna().all()}")
    print(f"  ✓ Valid email addresses: {df_customers['email'].str.contains('@').all()}")
    print(f"  ✓ Age range 18-80: {(df_customers['age'] >= 18).all() and (df_customers['age'] <= 80).all()}")

    print("\nProduct Data Quality:")
    print(f"  ✓ No duplicate product IDs: {df_products['product_id'].is_unique}")
    print(f"  ✓ Valid prices: {(df_products['price'] > 0).all()}")
    print(f"  ✓ Valid ratings 1-5: {(df_products['rating'] >= 1).all() and (df_products['rating'] <= 5).all()}")
    print(f"  ✓ Valid categories: {set(df_products['category']) == set(['Electronics', 'Clothing', 'Home', 'Sports', 'Books'])}")

    print("\nOrder Data Quality:")
    print(f"  ✓ No duplicate order IDs: {df_orders['order_id'].is_unique}")
    print(f"  ✓ Valid quantities 1-10: {(df_orders['quantity'] >= 1).all() and (df_orders['quantity'] <= 10).all()}")
    print(f"  ✓ All customers exist: {df_orders['customer_id'].isin(df_customers['customer_id']).all()}")
    print(f"  ✓ All products exist: {df_orders['product_id'].isin(df_products['product_id']).all()}")


def main() -> None:
    """Run all demonstrations."""
    try:
        # Run demos progressively
        print("\n" + "=" * 70)
        print("SYNTHETIC DATA GENERATOR DEMO")
        print("=" * 70)

        # Option 1: Small scale (quick)
        choice = input(
            "\nSelect demo to run:\n"
            "1. Small-scale (1K customers, 100 products, 10K orders) - QUICK\n"
            "2. Medium-scale (10K customers, 1K products, 100K orders)\n"
            "3. Large-scale (100K customers, 10K products, 1M orders) - RECOMMENDED\n"
            "4. All demos (sequential)\n"
            "\nEnter choice (1-4) [default: 1]: "
        ).strip()

        if choice == "2":
            demo_medium_scale()
        elif choice == "3":
            demo_large_scale()
        elif choice == "4":
            demo_small_scale()
            demo_medium_scale()
            # Note: Large scale might take several minutes
            response = input(
                "\nRun large-scale demo? This may take 5-10 minutes. (y/n) [default: n]: "
            )
            if response.lower() == "y":
                demo_large_scale()
        else:
            demo_small_scale()

        # Load and analyze the generated data
        config = Config()
        customers_file = config.get_raw_data_path(config.customers_file)
        if customers_file.exists():
            print("\n" + "=" * 70)
            print("LOADING AND ANALYZING GENERATED DATA")
            print("=" * 70)

            df_customers = pd.read_csv(customers_file)
            df_orders = pd.read_csv(config.get_raw_data_path(config.orders_file))

            demo_pareto_analysis(df_orders, len(df_customers))

            # Quality checks
            data = {
                "customers": df_customers,
                "products": pd.read_csv(config.get_raw_data_path(config.products_file)),
                "orders": df_orders,
            }
            demo_data_quality_checks(data)

        print("\n" + "=" * 70)
        print("✓ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Error during demo: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
