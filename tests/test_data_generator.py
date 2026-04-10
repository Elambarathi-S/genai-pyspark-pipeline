"""
Unit tests for the synthetic data generation module.
"""

import pytest
from pathlib import Path
import pandas as pd

from src.config import Config
from src.data_generator import SyntheticDataGenerator


class TestSyntheticDataGenerator:
    """Test suite for SyntheticDataGenerator class."""

    @pytest.fixture
    def config(self) -> Config:
        """Create a test configuration."""
        config = Config()
        return config

    @pytest.fixture
    def generator(self, config: Config) -> SyntheticDataGenerator:
        """Create a test generator with small dataset."""
        return SyntheticDataGenerator(
            config=config,
            num_customers=100,
            num_products=20,
            num_orders=500,
            seed=42
        )

    def test_generator_initialization(self, generator: SyntheticDataGenerator) -> None:
        """Test generator initialization."""
        assert generator.num_customers == 100
        assert generator.num_products == 20
        assert generator.num_orders == 500
        assert generator.seed == 42

    def test_generate_customers (self, generator: SyntheticDataGenerator) -> None:
        """Test customer generation."""
        df = generator.generate_customers()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        assert "customer_id" in df.columns
        assert "name" in df.columns
        assert "email" in df.columns
        assert "age" in df.columns
        assert "city" in df.columns
        assert "country" in df.columns
        assert "registration_date" in df.columns

        # Verify uniqueness
        assert df["customer_id"].is_unique
        assert df["email"].is_unique

        # Verify age constraints
        assert (df["age"] >= 18).all()
        assert (df["age"] <= 80).all()

    def test_generate_products(self, generator: SyntheticDataGenerator) -> None:
        """Test product generation."""
        df = generator.generate_products()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 20
        assert "product_id" in df.columns
        assert "name" in df.columns
        assert "category" in df.columns
        assert "price" in df.columns
        assert "stock" in df.columns
        assert "rating" in df.columns

        # Verify uniqueness
        assert df["product_id"].is_unique

        # Verify constraints
        assert (df["price"] > 0).all()
        assert (df["rating"] >= 1).all()
        assert (df["rating"] <= 5).all()
        assert (df["stock"] >= 0).all()

        # Verify categories
        valid_categories = {"Electronics", "Clothing", "Home", "Sports", "Books"}
        assert set(df["category"]).issubset(valid_categories)

    def test_generate_orders_with_pareto(self, generator: SyntheticDataGenerator) -> None:
        """Test order generation with Pareto distribution."""
        df_customers = generator.generate_customers()
        df_products = generator.generate_products()
        df_orders = generator.generate_orders_with_pareto(df_customers, df_products)

        assert isinstance(df_orders, pd.DataFrame)
        assert len(df_orders) == 500
        assert "order_id" in df_orders.columns
        assert "customer_id" in df_orders.columns
        assert "product_id" in df_orders.columns
        assert "quantity" in df_orders.columns
        assert "order_date" in df_orders.columns

        # Verify uniqueness
        assert df_orders["order_id"].is_unique

        # Verify constraints
        assert (df_orders["quantity"] >= 1).all()
        assert (df_orders["quantity"] <= 10).all()

        # Verify referential integrity
        assert df_orders["customer_id"].isin(df_customers["customer_id"]).all()
        assert df_orders["product_id"].isin(df_products["product_id"]).all()

        # Verify Pareto distribution (should be approximately 80/20)
        orders_per_customer = df_orders.groupby("customer_id").size()
        top_20_percent = int(len(df_customers) * 0.2)
        top_20_orders = orders_per_customer.nlargest(top_20_percent).sum()
        total_orders = len(df_orders)
        pareto_ratio = (top_20_orders / total_orders) * 100

        # Allow 10% deviation from 80%
        assert 70 <= pareto_ratio <= 90, f"Pareto ratio {pareto_ratio:.1f}% outside expected range"

    def test_save_data(self, generator: SyntheticDataGenerator, tmp_path: Path) -> None:
        """Test saving data to file."""
        df = generator.generate_customers()
        filename = "test_customers.csv"

        # Override data directory for test
        original_dir = generator.config.raw_data_dir
        generator.config.raw_data_dir = tmp_path

        filepath = generator.save_data(df, filename)

        assert filepath.exists()
        assert filepath.parent == tmp_path

        # Verify saved data
        loaded_df = pd.read_csv(filepath)
        assert len(loaded_df) == len(df)
        assert list(loaded_df.columns) == list(df.columns)

        # Restore original directory
        generator.config.raw_data_dir = original_dir

    def test_generate_and_save_all(self, generator: SyntheticDataGenerator) -> None:
        """Test complete data generation and saving pipeline."""
        data = generator.generate_and_save_all()

        # Verify returned dictionary
        assert isinstance(data, dict)
        assert "customers" in data
        assert "products" in data
        assert "orders" in data

        # Verify sizes
        assert len(data["customers"]) == 100
        assert len(data["products"]) == 20
        assert len(data["orders"]) == 500

        # Verify files were created
        assert generator.config.get_raw_data_path(
            generator.config.customers_file
        ).exists()
        assert generator.config.get_raw_data_path(
            generator.config.products_file
        ).exists()
        assert generator.config.get_raw_data_path(
            generator.config.orders_file
        ).exists()

    def test_reproducibility_with_seed(self, config: Config) -> None:
        """Test that same seed produces identical data."""
        gen1 = SyntheticDataGenerator(config, num_customers=50, num_products=10, num_orders=100, seed=42)
        data1 = gen1.generate_and_save_all()

        gen2 = SyntheticDataGenerator(config, num_customers=50, num_products=10, num_orders=100, seed=42)
        data2 = gen2.generate_and_save_all()

        # Check customers are identical
        pd.testing.assert_frame_equal(data1["customers"], data2["customers"])

        # Check products are identical
        pd.testing.assert_frame_equal(data1["products"], data2["products"])

        # Check orders are identical
        pd.testing.assert_frame_equal(data1["orders"], data2["orders"])

    def test_different_seeds_produce_different_data(self, config: Config) -> None:
        """Test that different seeds produce different data."""
        gen1 = SyntheticDataGenerator(config, num_customers=50, num_products=10, num_orders=100, seed=42)
        data1 = gen1.generate_and_save_all()

        gen2 = SyntheticDataGenerator(config, num_customers=50, num_products=10, num_orders=100, seed=123)
        data2 = gen2.generate_and_save_all()

        # Data should be different
        assert not data1["customers"]["name"].equals(data2["customers"]["name"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
