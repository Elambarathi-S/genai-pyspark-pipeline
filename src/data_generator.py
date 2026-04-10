"""
Synthetic data generation module for the e-commerce data pipeline.

This module provides the SyntheticDataGenerator class for generating large-scale,
realistic e-commerce data with proper statistical distributions using Faker,
NumPy, and pandas.
"""

import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import numpy as np
from faker import Faker
from tqdm import tqdm

from src.config import Config


class SyntheticDataGenerator:
    """
    Generate large-scale synthetic e-commerce data with realistic distributions.

    This class creates customers, products, and orders with:
    - Age distribution (normal distribution around 35)
    - Pareto distribution for customer orders (20% customers make 80% orders)
    - Realistic product categories and pricing
    - Progress tracking with tqdm
    """

    # Product categories
    CATEGORIES = ["Electronics", "Clothing", "Home", "Sports", "Books"]

    # Price ranges by category
    PRICE_RANGES = {
        "Electronics": (50, 500),
        "Clothing": (10, 150),
        "Home": (20, 300),
        "Sports": (15, 250),
        "Books": (8, 50),
    }

    def __init__(
        self,
        config: Config,
        num_customers: int = 100000,
        num_products: int = 10000,
        num_orders: int = 1000000,
        seed: int = 42,
    ) -> None:
        """
        Initialize the synthetic data generator.

        Args:
            config: Configuration object
            num_customers: Number of customers to generate (default: 100K)
            num_products: Number of products to generate (default: 10K)
            num_orders: Number of orders to generate (default: 1M)
            seed: Random seed for reproducibility (default: 42)
        """
        self.config = config
        self.num_customers = num_customers
        self.num_products = num_products
        self.num_orders = num_orders
        self.seed = seed

        # Set random seeds
        np.random.seed(seed)
        Faker.seed(seed)

        self.logger = logging.getLogger(__name__)
        self.fake = Faker()

        self.logger.info(
            f"Initialized SyntheticDataGenerator: "
            f"{num_customers:,} customers, "
            f"{num_products:,} products, "
            f"{num_orders:,} orders"
        )

    def generate_customers(self) -> pd.DataFrame:
        """
        Generate synthetic customer data with realistic demographics.

        Age is generated from a normal distribution centered around 35 years.
        Registration dates span the last 2 years.

        Returns:
            DataFrame with columns: customer_id, name, email, age, city, country, registration_date
        """
        self.logger.info(f"Generating {self.num_customers:,} customers...")

        customers_data = {
            "customer_id": range(1, self.num_customers + 1),
            "name": [self.fake.name() for _ in tqdm(range(self.num_customers), desc="Generating customer names")],
            "email": [
                self.fake.unique.email()
                for _ in tqdm(range(self.num_customers), desc="Generating customer emails")
            ],
            "age": np.random.normal(loc=35, scale=12, size=self.num_customers).astype(int),
            "city": [
                self.fake.city()
                for _ in tqdm(range(self.num_customers), desc="Generating customer cities")
            ],
            "country": [
                self.fake.country()
                for _ in tqdm(range(self.num_customers), desc="Generating customer countries")
            ],
            "registration_date": [
                self.fake.date_between(start_date="-2y")
                for _ in tqdm(range(self.num_customers), desc="Generating registration dates")
            ],
        }

        df_customers = pd.DataFrame(customers_data)

        # Ensure age is within reasonable bounds
        df_customers["age"] = df_customers["age"].clip(lower=18, upper=80)

        self.logger.info(f"✓ Generated {len(df_customers):,} customers")
        self.logger.info(f"  Age stats: mean={df_customers['age'].mean():.1f}, std={df_customers['age'].std():.1f}")

        return df_customers

    def generate_products(self) -> pd.DataFrame:
        """
        Generate synthetic product data with realistic categories and pricing.

        Products are distributed across 5 categories with category-specific
        price ranges. Ratings are between 1-5.

        Returns:
            DataFrame with columns: product_id, name, category, price, stock, rating
        """
        self.logger.info(f"Generating {self.num_products:,} products...")

        products_data = []

        for product_id in tqdm(range(1, self.num_products + 1), desc="Generating products"):
            category = np.random.choice(self.CATEGORIES)
            price_min, price_max = self.PRICE_RANGES[category]

            product = {
                "product_id": product_id,
                "name": f"{self.fake.word().title()} {self.fake.word().title()}",
                "category": category,
                "price": np.random.uniform(price_min, price_max),
                "stock": np.random.randint(0, 1000),
                "rating": np.random.uniform(1, 5),
            }
            products_data.append(product)

        df_products = pd.DataFrame(products_data)
        df_products["price"] = df_products["price"].round(2)
        df_products["rating"] = df_products["rating"].round(2)

        self.logger.info(f"✓ Generated {len(df_products):,} products")
        self.logger.info(f"  Category distribution:\n{df_products['category'].value_counts().to_string()}")

        return df_products

    def generate_orders_with_pareto(
        self, df_customers: pd.DataFrame, df_products: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate orders with Pareto distribution (80/20 rule).

        80% of orders are made by 20% of customers. This is achieved by
        sampling customer IDs from a Pareto distribution.

        Args:
            df_customers: Customer DataFrame
            df_products: Product DataFrame

        Returns:
            DataFrame with columns: order_id, customer_id, product_id, quantity, order_date
        """
        self.logger.info(f"Generating {self.num_orders:,} orders with Pareto distribution (80/20)...")

        # Generate Pareto-distributed customer indices (concentration on top 20%)
        # Pareto distribution: 80% of orders from 20% of customers
        pareto_shape = 1.16  # Shape parameter for Pareto distribution
        customer_indices = np.random.pareto(pareto_shape, size=self.num_orders)
        customer_indices = (customer_indices / customer_indices.max() * (self.num_customers - 1)).astype(int)
        customer_ids = df_customers.iloc[customer_indices]["customer_id"].values

        # Generate random product IDs
        product_ids = np.random.choice(df_products["product_id"].values, size=self.num_orders)

        # Generate order dates (last 1 year)
        order_dates = [
            self.fake.date_between(start_date="-1y")
            for _ in tqdm(range(self.num_orders), desc="Generating order dates")
        ]

        # Generate quantities (1-10)
        quantities = np.random.randint(1, 11, size=self.num_orders)

        orders_data = {
            "order_id": range(1, self.num_orders + 1),
            "customer_id": customer_ids,
            "product_id": product_ids,
            "quantity": quantities,
            "order_date": order_dates,
        }

        df_orders = pd.DataFrame(orders_data)

        # Verify Pareto distribution
        orders_per_customer = df_orders.groupby("customer_id").size()
        top_20_percent_customers = int(self.num_customers * 0.2)
        top_20_orders = orders_per_customer.nlargest(top_20_percent_customers).sum()
        pareto_ratio = (top_20_orders / self.num_orders) * 100

        self.logger.info(f"✓ Generated {len(df_orders):,} orders")
        self.logger.info(f"  Pareto ratio: {pareto_ratio:.1f}% of orders from top 20% of customers")

        return df_orders

    def save_data(self, df: pd.DataFrame, filename: str) -> Path:
        """
        Save DataFrame to CSV file with compression.

        Args:
            df: DataFrame to save
            filename: Name of the output file

        Returns:
            Path to the saved file
        """
        filepath = self.config.get_raw_data_path(filename)
        df.to_csv(filepath, index=False)
        file_size_mb = filepath.stat().st_size / (1024 * 1024)
        self.logger.info(f"✓ Saved {filename} ({len(df):,} rows, {file_size_mb:.2f} MB)")
        return filepath

    def generate_and_save_all(self) -> Dict[str, pd.DataFrame]:
        """
        Generate all synthetic data and save to CSV files.

        Returns:
            Dictionary containing DataFrames for customers, products, and orders
        """
        self.logger.info("=" * 70)
        self.logger.info("STARTING SYNTHETIC DATA GENERATION")
        self.logger.info("=" * 70)
        self.config.log_config()

        # Generate data
        df_customers = self.generate_customers()
        df_products = self.generate_products()
        df_orders = self.generate_orders_with_pareto(df_customers, df_products)

        # Save data
        self.logger.info("\n" + "=" * 70)
        self.logger.info("SAVING DATA TO CSV")
        self.logger.info("=" * 70)

        self.save_data(df_customers, self.config.customers_file)
        self.save_data(df_products, self.config.products_file)
        self.save_data(df_orders, self.config.orders_file)

        self.logger.info("\n" + "=" * 70)
        self.logger.info("✓ SYNTHETIC DATA GENERATION COMPLETED SUCCESSFULLY!")
        self.logger.info("=" * 70)

        return {
            "customers": df_customers,
            "products": df_products,
            "orders": df_orders,
        }

    def get_data_summary(
        self, df_customers: pd.DataFrame, df_products: pd.DataFrame, df_orders: pd.DataFrame
    ) -> None:
        """
        Log summary statistics of generated data.

        Args:
            df_customers: Customer DataFrame
            df_products: Product DataFrame
            df_orders: Order DataFrame
        """
        self.logger.info("\n" + "=" * 70)
        self.logger.info("DATA SUMMARY STATISTICS")
        self.logger.info("=" * 70)

        self.logger.info("\nCustomers:")
        self.logger.info(f"  Total: {len(df_customers):,}")
        self.logger.info(f"  Age range: {df_customers['age'].min()} - {df_customers['age'].max()}")
        self.logger.info(f"  Unique countries: {df_customers['country'].nunique()}")

        self.logger.info("\nProducts:")
        self.logger.info(f"  Total: {len(df_products):,}")
        self.logger.info(f"  Categories: {', '.join(df_products['category'].unique())}")
        self.logger.info(f"  Price range: ${df_products['price'].min():.2f} - ${df_products['price'].max():.2f}")
        self.logger.info(f"  Avg rating: {df_products['rating'].mean():.2f}")

        self.logger.info("\nOrders:")
        self.logger.info(f"  Total: {len(df_orders):,}")
        orders_per_customer = df_orders.groupby("customer_id").size()
        self.logger.info(f"  Avg orders per customer: {orders_per_customer.mean():.2f}")
        self.logger.info(f"  Max orders per customer: {orders_per_customer.max()}")
        self.logger.info(f"  Quantity per order: {df_orders['quantity'].mean():.2f} avg")


# Legacy compatibility class
class DataGenerator(SyntheticDataGenerator):
    """
    Legacy compatibility wrapper for DataGenerator.

    This class maintains backward compatibility with the original DataGenerator API.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize DataGenerator with config settings.

        Args:
            config: Configuration object
        """
        super().__init__(
            config=config,
            num_customers=config.num_customers,
            num_products=config.num_products,
            num_orders=config.num_orders,
        )

    def generate_all(self) -> None:
        """Generate all data files and save them."""
        self.generate_and_save_all()
