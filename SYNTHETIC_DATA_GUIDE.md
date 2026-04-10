# SyntheticDataGenerator - Complete Usage Guide

## Overview

The `SyntheticDataGenerator` class generates large-scale, realistic e-commerce data with proper statistical distributions. It's designed to create synthetic datasets suitable for testing, development, and analysis.

## Features

✅ **Large-Scale Data Generation**
- Default: 100K customers, 10K products, 1M orders
- Customizable scales from small (1K/100/10K) to massive datasets
- Progress tracking with `tqdm` progress bars

✅ **Realistic Data Distributions**
- Customer age: Normal distribution centered around 35 years
- Customer orders: Pareto distribution (80/20 rule)
  - 20% of customers make 80% of orders
- Product prices: Category-specific price ranges
- Product ratings: 1-5 scale

✅ **Data Quality**
- Type hints on all functions
- Comprehensive docstrings
- Logging at every step
- Data validation and constraints
- Reproducible results (seeded randomization)

✅ **Efficient Data Generation**
- NumPy for statistical distributions
- Faker for realistic names and dates
- Pandas DataFrames for easy manipulation
- CSV export with file size tracking

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

Key packages:
- `faker==21.0.0` - Generate realistic names, emails, dates
- `numpy==1.24.3` - Statistical distributions
- `pandas==2.1.4` - Data manipulation
- `tqdm==4.66.1` - Progress bars

## Quick Start

### 1. Generate Default Dataset (100K/10K/1M)

```python
from src.config import Config
from src.data_generator import SyntheticDataGenerator

# Initialize
config = Config()
generator = SyntheticDataGenerator(config)

# Generate and save
data = generator.generate_and_save_all()

# Access data
df_customers = data['customers']
df_products = data['products']
df_orders = data['orders']
```

### 2. Generate Custom Sizes

```python
# Small dataset for testing
generator = SyntheticDataGenerator(
    config=config,
    num_customers=1000,
    num_products=100,
    num_orders=10000
)
data = generator.generate_and_save_all()

# Medium dataset
generator = SyntheticDataGenerator(
    config=config,
    num_customers=10000,
    num_products=1000,
    num_orders=100000
)
data = generator.generate_and_save_all()

# Large dataset (default)
generator = SyntheticDataGenerator(
    config=config,
    num_customers=100000,
    num_products=10000,
    num_orders=1000000
)
data = generator.generate_and_save_all()
```

### 3. Get Data Summary

```python
# Get comprehensive statistics
generator.get_data_summary(
    data['customers'],
    data['products'],
    data['orders']
)
```

## Data Schema

### Customers

```
customer_id    : int     - Unique customer identifier (1 to num_customers)
name           : str     - Customer full name
email          : str     - Customer email address (unique)
age            : int     - Age (normal distribution, centered at 35, range 18-80)
city           : str     - Customer city
country        : str     - Customer country
registration_date : date - Registration date (last 2 years)
```

Example:
```
customer_id | name              | email              | age | city      | country | registration_date
1           | John Smith        | john@example.com   | 42  | New York  | USA     | 2024-06-15
2           | Jane Doe          | jane@example.com   | 35  | London    | UK      | 2024-03-20
```

### Products

```
product_id : int     - Unique product identifier (1 to num_products)
name       : str     - Product name
category   : str     - Category (Electronics, Clothing, Home, Sports, Books)
price      : float   - Price ($) - category specific ranges
stock      : int     - Stock quantity (0-1000)
rating     : float   - Rating (1-5)
```

Category Price Ranges:
- **Electronics**: $50 - $500
- **Clothing**: $10 - $150
- **Home**: $20 - $300
- **Sports**: $15 - $250
- **Books**: $8 - $50

Example:
```
product_id | name              | category     | price | stock | rating
1          | Wireless Headset  | Electronics  | 89.99 | 245   | 4.32
2          | Cotton T-Shirt    | Clothing     | 24.99 | 512   | 3.87
```

### Orders

```
order_id       : int  - Unique order identifier (1 to num_orders)
customer_id    : int  - Customer ID (foreign key to customers)
product_id     : int  - Product ID (foreign key to products)
quantity       : int  - Order quantity (1-10)
order_date     : date - Order date (last 1 year)
```

Example:
```
order_id | customer_id | product_id | quantity | order_date
1        | 42          | 156        | 3        | 2025-08-10
2        | 15          | 789        | 1        | 2025-08-11
```

## Pareto Distribution (80/20 Rule)

The order generation implements the Pareto principle:
- **20% top customers** generate approximately **80% of all orders**
- Achieved using NumPy's Pareto distribution

### Example

```
Total Customers: 100,000
Orders by Top 20% (20,000 customers): ~800,000 out of 1,000,000
Pareto Ratio: ~80%
```

### Verify Pareto Distribution

```python
# After generation
orders_per_customer = df_orders.groupby('customer_id').size()

# Top 20% statistics
top_20_percent = int(len(df_customers) * 0.2)
top_20_orders = orders_per_customer.nlargest(top_20_percent).sum()
total_orders = len(df_orders)
pareto_ratio = (top_20_orders / total_orders) * 100

print(f"Pareto Ratio: {pareto_ratio:.1f}%")
```

## Class Methods

### `__init__(config, num_customers=100000, num_products=10000, num_orders=1000000, seed=42)`

Initialize the generator with configuration and dataset sizes.

**Parameters:**
- `config` (Config): Configuration object
- `num_customers` (int): Number of customers to generate
- `num_products` (int): Number of products to generate
- `num_orders` (int): Number of orders to generate
- `seed` (int): Random seed for reproducibility

### `generate_customers() -> DataFrame`

Generate customer data with demographic information.

**Returns:** DataFrame with customer data

**Column Details:**
- Age: Normal distribution (μ=35, σ=12), clipped to 18-80
- Registration: Random dates in last 2 years
- Email: Unique using Faker

### `generate_products() -> DataFrame`

Generate product data with categories and pricing.

**Returns:** DataFrame with product data

**Features:**
- 5 product categories
- Category-specific price ranges
- Random stock (0-1000)
- Rating from 1-5

### `generate_orders_with_pareto(df_customers, df_products) -> DataFrame`

Generate orders with Pareto distribution (80/20 rule).

**Parameters:**
- `df_customers` (DataFrame): Customer DataFrame
- `df_products` (DataFrame): Product DataFrame

**Returns:** DataFrame with order data

**Distribution:**
- Customer selection: Pareto distribution
- Quantities: Uniform 1-10
- Dates: Last 1 year

### `save_data(df, filename) -> Path`

Save DataFrame to CSV file with logging.

**Parameters:**
- `df` (DataFrame): DataFrame to save
- `filename` (str): Output filename

**Returns:** Path to saved file

### `generate_and_save_all() -> Dict[str, DataFrame]`

Generate all data and save to CSV files.

**Returns:** Dictionary with 'customers', 'products', 'orders' DataFrames

### `get_data_summary(df_customers, df_products, df_orders) -> None`

Log comprehensive summary statistics.

**Parameters:**
- `df_customers` (DataFrame): Customer DataFrame
- `df_products` (DataFrame): Product DataFrame
- `df_orders` (DataFrame): Order DataFrame

## Performance Characteristics

### Generation Time Estimates

| Scale | Customers | Products | Orders | Est. Time | Data Size |
|-------|-----------|----------|--------|-----------|-----------|
| Small | 1K | 100 | 10K | < 1 min | ~500 KB |
| Medium | 10K | 1K | 100K | 2-3 min | ~5 MB |
| Large | 100K | 10K | 1M | 5-10 min | ~50 MB |
| XL | 1M | 100K | 10M | 1-2 hours | ~500 MB |

Est. times on modern hardware (i7/16GB RAM)

### Memory Usage

- Small: ~100 MB RAM
- Medium: ~500 MB RAM
- Large: ~1-2 GB RAM
- XL: ~5-10 GB RAM

## Example Usage Scripts

### Simple Generation

```python
from src.config import Config
from src.data_generator import SyntheticDataGenerator

config = Config()
generator = SyntheticDataGenerator(config)
data = generator.generate_and_save_all()

print(f"Generated {len(data['customers']):,} customers")
print(f"Generated {len(data['products']):,} products")
print(f"Generated {len(data['orders']):,} orders")
```

### With Analysis

```python
from src.config import Config
from src.data_generator import SyntheticDataGenerator
import pandas as pd

config = Config()
generator = SyntheticDataGenerator(
    config=config,
    num_customers=5000,
    num_products=500,
    num_orders=50000
)

data = generator.generate_and_save_all()
generator.get_data_summary(
    data['customers'],
    data['products'],
    data['orders']
)

# Analyze Pareto distribution
orders = data['orders'].groupby('customer_id').size()
top_20 = orders.nlargest(int(len(data['customers']) * 0.2)).sum()
print(f"Top 20% customers: {top_20 / len(data['orders']) * 100:.1f}%")
```

### Custom Seed for Reproducibility

```python
# Generate identical data with same seed
generator1 = SyntheticDataGenerator(config, seed=42)
data1 = generator1.generate_and_save_all()

generator2 = SyntheticDataGenerator(config, seed=42)
data2 = generator2.generate_and_save_all()

# data1 and data2 are identical
```

## Using with PySpark

```python
from src.config import Config
from src.data_generator import SyntheticDataGenerator
from src.spark_analytics import SparkAnalytics

# Generate data
config = Config()
generator = SyntheticDataGenerator(config)
generator.generate_and_save_all()

# Analyze with Spark
analytics = SparkAnalytics(config)
results = analytics.analyze()
```

## Data Quality Guarantees

✓ **No Duplicates**: Customer IDs and Product IDs are unique  
✓ **Referential Integrity**: All order customer_id and product_id references exist  
✓ **Valid Ranges**: Ages 18-80, ratings 1-5, quantities 1-10  
✓ **Valid Categories**: Only valid product categories used  
✓ **Valid Emails**: All emails contain '@' symbol  
✓ **Realistic Dates**: Dates are within reasonable historical bounds

## Backward Compatibility

The legacy `DataGenerator` class is available for backward compatibility:

```python
from src.data_generator import DataGenerator
from src.config import Config

config = Config()
generator = DataGenerator(config=config)
generator.generate_all()
```

This uses the same interface as the original implementation.

## Tips & Best Practices

1. **Start Small**: Test with small datasets first to validate your code
2. **Use Seeds**: Set seed for reproducible results
3. **Monitor Progress**: Watch the progress bars during generation
4. **Check Logs**: Review logging output for data statistics
5. **Validate Data**: Always run quality checks on generated data
6. **Memory Aware**: Be mindful of available RAM for large datasets
7. **Parallel Processing**: Use generated data with PySpark for analysis

## Troubleshooting

### Out of Memory

- Generate smaller dataset first
- Reduce batch sizes
- Increase system swap

### Slow Generation

- Normal for large datasets (1M+ orders)
- Use smaller scales for development
- Consider using SSD for CSV writes

### Non-reproducible Results

- Always set seed parameter
- Faker and NumPy both use the seed
- Same seed = identical data

## Related Documentation

- [README.md](README.md) - Project overview
- [src/config.py](src/config.py) - Configuration settings
- [src/spark_analytics.py](src/spark_analytics.py) - PySpark analysis
- [demo_synthetic_data.py](demo_synthetic_data.py) - Demo script
