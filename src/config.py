"""
Configuration module for the e-commerce data pipeline.

This module contains all configuration settings for data generation,
processing, and analysis.
"""

import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Config:
    """Configuration class for the data pipeline."""

    def __init__(self) -> None:
        """Initialize configuration settings."""
        # Project paths
        self.project_root: Path = Path(__file__).parent.parent
        self.data_dir: Path = self.project_root / "data"
        self.raw_data_dir: Path = self.data_dir / "raw"
        self.processed_data_dir: Path = self.data_dir / "processed"
        self.notebooks_dir: Path = self.project_root / "notebooks"

        # Ensure directories exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)

        # Data generation settings
        self.num_customers: int = 1000
        self.num_products: int = 500
        self.num_orders: int = 5000
        self.num_order_items_per_order: int = 3

        # File names
        self.customers_file: str = "customers.csv"
        self.products_file: str = "products.csv"
        self.orders_file: str = "orders.csv"
        self.order_items_file: str = "order_items.csv"

        # Output files
        self.summary_report_file: str = "summary_report.csv"
        self.customer_insights_file: str = "customer_insights.csv"
        self.product_performance_file: str = "product_performance.csv"

        # Logging
        self.logger: logging.Logger = logging.getLogger(__name__)

    def get_raw_data_path(self, filename: str) -> Path:
        """
        Get the full path for a raw data file.

        Args:
            filename: Name of the file in raw data directory

        Returns:
            Path to the raw data file
        """
        return self.raw_data_dir / filename

    def get_processed_data_path(self, filename: str) -> Path:
        """
        Get the full path for a processed data file.

        Args:
            filename: Name of the file in processed data directory

        Returns:
            Path to the processed data file
        """
        return self.processed_data_dir / filename

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "project_root": str(self.project_root),
            "num_customers": self.num_customers,
            "num_products": self.num_products,
            "num_orders": self.num_orders,
            "num_order_items_per_order": self.num_order_items_per_order,
        }

    def log_config(self) -> None:
        """Log the current configuration settings."""
        self.logger.info("Configuration Settings:")
        self.logger.info(f"  Project Root: {self.project_root}")
        self.logger.info(f"  Data Directory: {self.data_dir}")
        self.logger.info(f"  Number of Customers: {self.num_customers}")
        self.logger.info(f"  Number of Products: {self.num_products}")
        self.logger.info(f"  Number of Orders: {self.num_orders}")
