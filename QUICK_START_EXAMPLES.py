"""
Quick Start Examples for SyntheticDataGenerator
"""

# ============================================================================
# EXAMPLE 1: Generate data with default settings (100K, 10K, 1M)
# ============================================================================

from src.config import Config
from src.data_generator import SyntheticDataGenerator

config = Config()
generator = SyntheticDataGenerator(config)
data = generator.generate_and_save_all()

print(f"✓ Generated {len(data['customers']):,} customers")
print(f"✓ Generated {len(data['products']):,} products")
print(f"✓ Generated {len(data['orders']):,} orders")


# ============================================================================
# EXAMPLE 2: Generate small dataset for testing
# ============================================================================

config = Config()
generator = SyntheticDataGenerator(
    config=config,
    num_customers=1000,
    num_products=100,
    num_orders=10000
)
data = generator.generate_and_save_all()


# ============================================================================
# EXAMPLE 3: Custom seed for reproducibility
# ============================================================================

config1 = Config()
gen1 = SyntheticDataGenerator(config1, seed=42)
data1 = gen1.generate_and_save_all()

config2 = Config()
gen2 = SyntheticDataGenerator(config2, seed=42)
data2 = gen2.generate_and_save_all()

# data1 and data2 are identical
print(data1['customers'].equals(data2['customers']))  # True


# ============================================================================
# EXAMPLE 4: Access and inspect data
# ============================================================================

df_customers = data['customers']
print(df_customers.head())
print(f"Age statistics:")
print(df_customers['age'].describe())

df_products = data['products']
print(df_products['category'].value_counts())

df_orders = data['orders']
print(f"Orders per customer: {df_orders.groupby('customer_id').size().describe()}")


# ============================================================================
# EXAMPLE 5: Verify Pareto distribution (80/20 rule)
# ============================================================================

orders_per_customer = df_orders.groupby('customer_id').size()
top_20_percent_count = int(len(df_customers) * 0.2)
top_20_orders = orders_per_customer.nlargest(top_20_percent_count).sum()
total_orders = len(df_orders)
pareto_ratio = (top_20_orders / total_orders) * 100

print(f"Top 20% of customers: {top_20_percent_count:,}")
print(f"Orders by top 20%: {top_20_orders:,} / {total_orders:,}")
print(f"Pareto ratio: {pareto_ratio:.1f}%")


# ============================================================================
# EXAMPLE 6: Data quality checks
# ============================================================================

# Check for duplicates
print(f"Unique customers: {df_customers['customer_id'].is_unique}")
print(f"Unique products: {df_products['product_id'].is_unique}")
print(f"Unique orders: {df_orders['order_id'].is_unique}")

# Check referential integrity
print(f"All orders reference valid customers: {df_orders['customer_id'].isin(df_customers['customer_id']).all()}")
print(f"All orders reference valid products: {df_orders['product_id'].isin(df_products['product_id']).all()}")

# Check data constraints
print(f"Valid ages (18-80): {((df_customers['age'] >= 18) & (df_customers['age'] <= 80)).all()}")
print(f"Valid ratings (1-5): {((df_products['rating'] >= 1) & (df_products['rating'] <= 5)).all()}")
print(f"Valid quantities (1-10): {((df_orders['quantity'] >= 1) & (df_orders['quantity'] <= 10)).all()}")


# ============================================================================
# EXAMPLE 7: Save to different formats
# ============================================================================

# Already saved as CSV, but can also:
# Save to Parquet (more efficient for large datasets)
df_customers.to_parquet('customers.parquet')
df_products.to_parquet('products.parquet')
df_orders.to_parquet('orders.parquet')

# Save to Excel (not recommended for large datasets)
# df_customers.to_excel('customers.xlsx', index=False)

# Save to JSON
df_customers.head(100).to_json('customers_sample.json', orient='records')


# ============================================================================
# EXAMPLE 8: Use with PySpark for analysis
# ============================================================================

from src.spark_analytics import SparkAnalytics

config = Config()
generator = SyntheticDataGenerator(config)
generator.generate_and_save_all()

# Analyze with Spark
analytics = SparkAnalytics(config)
results = analytics.analyze()

# Results contain: Summary Statistics, Customer Insights, Product Performance,
# Order Status Distribution, Category Performance
print(results['Summary Statistics'])


# ============================================================================
# EXAMPLE 9: Generate multiple datasets for A/B testing
# ============================================================================

seeds = [42, 123, 456]
datasets = []

for seed in seeds:
    config = Config()
    generator = SyntheticDataGenerator(config, seed=seed)
    data = generator.generate_and_save_all()
    datasets.append(data)

# Each dataset is identical in structure but different in content
print(f"Generated {len(datasets)} datasets")


# ============================================================================
# EXAMPLE 10: Filter and analyze specific customer segments
# ============================================================================

# Find high-value customers (top 10% by age)
age_threshold = df_customers['age'].quantile(0.9)
high_age_customers = df_customers[df_customers['age'] >= age_threshold]

# Orders from high-age customers
high_age_orders = df_orders[df_orders['customer_id'].isin(high_age_customers['customer_id'])]

print(f"High-age customers: {len(high_age_customers)}")
print(f"Orders from them: {len(high_age_orders)}")

# Find most popular categories
category_popularity = df_orders.merge(
    df_products[['product_id', 'category']],
    on='product_id'
)['category'].value_counts()

print(category_popularity)
