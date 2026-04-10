"""
Main entry point for the e-commerce data pipeline.

This script demonstrates:
1. Generating synthetic data with proper statistical distributions
2. Pareto distribution for customer orders (80/20 rule)
3. Running analytics on the generated data
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.data_generator import SyntheticDataGenerator
from src.spark_analytics import SparkAnalytics


def main() -> None:
    """Run the complete e-commerce data pipeline."""
    print("=" * 80)
    print("E-COMMERCE DATA PIPELINE - SYNTHETIC DATA GENERATION & ANALYSIS")
    print("=" * 80)

    # Initialize configuration
    config = Config()

    # Step 1: Generate synthetic data
    print("\n" + "=" * 80)
    print("STEP 1: GENERATING SYNTHETIC DATA")
    print("=" * 80)

    generator = SyntheticDataGenerator(
        config=config,
        num_customers=100000,
        num_products=10000,
        num_orders=1000000,
    )

    data = generator.generate_and_save_all()
    generator.get_data_summary(
        data['customers'],
        data['products'],
        data['orders']
    )

    # Step 2: Analyze Pareto distribution
    print("\n" + "=" * 80)
    print("STEP 2: PARETO DISTRIBUTION ANALYSIS (80/20 Rule)")
    print("=" * 80)

    orders_per_customer = data['orders'].groupby('customer_id').size()
    top_20_percent = int(len(data['customers']) * 0.2)
    top_20_orders = orders_per_customer.nlargest(top_20_percent).sum()
    pareto_ratio = (top_20_orders / len(data['orders'])) * 100

    print(f"\nCustomer Statistics:")
    print(f"  Total customers: {len(data['customers']):,}")
    print(f"  Top 20%: {top_20_percent:,}")

    print(f"\nOrder Statistics:")
    print(f"  Total orders: {len(data['orders']):,}")
    print(f"  Orders by top 20%: {top_20_orders:,}")
    print(f"  Pareto ratio: {pareto_ratio:.1f}%")
    print(f"  Expected ratio: ~80%")

    # Step 3: Run analytics
    print("\n" + "=" * 80)
    print("STEP 3: RUNNING ANALYTICS WITH PYSPARK")
    print("=" * 80)

    analytics = SparkAnalytics(config)

    try:
        results = analytics.analyze()

        # Display summary results
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)

        print("\n--- Summary Statistics ---")
        print(results["Summary Statistics"].to_string(index=False))

        print("\n--- Top 10 Customers by Spending ---")
        print(
            results["Customer Insights"][
                ["customer_id", "name", "total_spent", "total_orders"]
            ]
            .head(10)
            .to_string(index=False)
        )

        print("\n--- Top 10 Products by Revenue ---")
        print(
            results["Product Performance"][
                ["product_id", "product_name", "category", "total_revenue"]
            ]
            .head(10)
            .to_string(index=False)
        )

        print("\n--- Order Status Distribution ---")
        print(results["Order Status Distribution"].to_string(index=False))

        print("\n--- Category Performance ---")
        print(results["Category Performance"].to_string(index=False))

        print("\n" + "=" * 80)
        print("✓ PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nResults saved to: {config.processed_data_dir}")
        print(f"Raw data saved to: {config.raw_data_dir}")

    finally:
        analytics.stop()


if __name__ == "__main__":
    main()
