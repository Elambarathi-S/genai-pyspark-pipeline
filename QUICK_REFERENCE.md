# SyntheticDataGenerator - Quick Reference Card

## Import
```python
from src.data_generator import SyntheticDataGenerator
from src.config import Config
```

## Initialize
```python
config = Config()

# Default: 100K customers, 10K products, 1M orders
generator = SyntheticDataGenerator(config)

# Custom scale
generator = SyntheticDataGenerator(
    config=config,
    num_customers=1000,
    num_products=100,
    num_orders=10000,
    seed=42  # For reproducibility
)
```

## Generate Data
```python
# Generate and save (returns dict with DataFrames)
data = generator.generate_and_save_all()

# Access data
df_customers = data['customers']
df_products = data['products']
df_orders = data['orders']
```

## Inspect Data
```python
# Display summary
generator.get_data_summary(
    data['customers'],
    data['products'],
    data['orders']
)

# View samples
df_customers.head()
df_products.head()
df_orders.head()

# Statistics
df_customers['age'].describe()
df_products['price'].describe()
df_orders['quantity'].value_counts()
```

## Pareto Distribution (80/20)
```python
orders_per_customer = df_orders.groupby('customer_id').size()

# Calculate ratio
top_20_percent = int(len(df_customers) * 0.2)
top_20_orders = orders_per_customer.nlargest(top_20_percent).sum()
ratio = (top_20_orders / len(df_orders)) * 100

print(f"Pareto ratio: {ratio:.1f}%")  # Expected: ~80%
```

## Data Quality Checks
```python
# Check for duplicates
df_customers['customer_id'].is_unique      # Should be True
df_products['product_id'].is_unique         # Should be True
df_orders['order_id'].is_unique             # Should be True

# Check constraints
assert (df_customers['age'] >= 18).all()    # Age > 18
assert (df_customers['age'] <= 80).all()    # Age < 80
assert (df_products['rating'] >= 1).all()   # Rating > 1
assert (df_products['rating'] <= 5).all()   # Rating < 5
assert (df_orders['quantity'] >= 1).all()   # Quantity > 1
assert (df_orders['quantity'] <= 10).all()  # Quantity < 10

# Check referential integrity
df_orders['customer_id'].isin(df_customers['customer_id']).all()
df_orders['product_id'].isin(df_products['product_id']).all()
```

## Data Schemas

### Customers
| Field | Type | Notes |
|-------|------|-------|
| customer_id | int | 1 to num_customers |
| name | str | Realistic full name |
| email | str | Unique email |
| age | int | Normal dist. ~35, range 18-80 |
| city | str | Random city |
| country | str | Random country |
| registration_date | date | Last 2 years |

### Products
| Field | Type | Notes |
|-------|------|-------|
| product_id | int | 1 to num_products |
| name | str | Generated product name |
| category | str | Electronics, Clothing, Home, Sports, Books |
| price | float | Category-specific range |
| stock | int | 0-1000 |
| rating | float | 1-5 |

### Orders
| Field | Type | Notes |
|-------|------|-------|
| order_id | int | 1 to num_orders |
| customer_id | int | Foreign key |
| product_id | int | Foreign key |
| quantity | int | 1-10 |
| order_date | date | Last 1 year |

## Category Price Ranges
```
Electronics: $50 - $500
Clothing:    $10 - $150
Home:        $20 - $300
Sports:      $15 - $250
Books:       $8 - $50
```

## Common Tasks

### Find Top Customers
```python
top_customers = df_orders.groupby('customer_id')['customer_id'].count().nlargest(10)
df_orders[df_orders['customer_id'].isin(top_customers.index)]
```

### Find Top Products
```python
top_products = df_orders.groupby('product_id')['product_id'].count().nlargest(10)
df_orders[df_orders['product_id'].isin(top_products.index)]
```

### Find Top Categories
```python
category_orders = df_orders.merge(
    df_products[['product_id', 'category']],
    on='product_id'
)['category'].value_counts()
```

### Calculate Total Revenue
```python
df_orders.merge(
    df_products[['product_id', 'price']],
    on='product_id'
).assign(revenue=lambda x: x['quantity'] * x['price'])['revenue'].sum()
```

### Find High-Value Customers
```python
revenue_by_customer = df_orders.merge(
    df_products[['product_id', 'price']],
    on='product_id'
).assign(revenue=lambda x: x['quantity'] * x['price']).groupby('customer_id')['revenue'].sum()

high_value = revenue_by_customer[revenue_by_customer > revenue_by_customer.quantile(0.9)]
```

### Analyze by Registration Age
```python
df_customers['days_since_registration'] = (
    pd.Timestamp.now() - pd.to_datetime(df_customers['registration_date'])
).dt.days

df_customers.groupby('customer_segment')['days_since_registration'].mean()
```

## File Locations
```python
from src.config import Config

config = Config()

# Raw data
config.raw_data_dir            # data/raw/
config.get_raw_data_path('customers.csv')

# Processed data
config.processed_data_dir      # data/processed/
config.get_processed_data_path('results.csv')
```

## Tests
```bash
# Run all tests
pytest tests/test_data_generator.py -v

# Run specific test
pytest tests/test_data_generator.py::TestSyntheticDataGenerator::test_generate_customers -v

# Run with coverage
pytest tests/test_data_generator.py --cov=src --cov-report=html
```

## Performance
```
Small (1K/100/10K):      < 1 min,   500 KB
Medium (10K/1K/100K):    2-3 min,   5 MB
Large (100K/10K/1M):     5-10 min,  50 MB
XL (1M/100K/10M):        1-2 hours, 500 MB
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Out of Memory | Generate smaller dataset or close other apps |
| Slow generation | Normal for 1M+ records; use smaller scale for testing |
| Non-reproducible | Set seed parameter: `SyntheticDataGenerator(..., seed=42)` |
| Import error | Install deps: `pip install -r requirements.txt` |
| File not found | Check `config.raw_data_dir` path exists |

## Advanced: Custom Modifications

### Change Age Distribution
```python
# In generate_customers():
df['age'] = np.random.normal(loc=40, scale=15, size=len_customers)  # Center at 40
```

### Change Price Distribution
```python
# In generate_products():
price = np.random.exponential(scale=100)  # Exponential instead of uniform
```

### Change Pareto Parameter
```python
# In generate_orders_with_pareto():
pareto_shape = 2.0  # Higher = more concentrated
```

## Full Example
```python
from src.config import Config
from src.data_generator import SyntheticDataGenerator
import pandas as pd

# Initialize
config = Config()
generator = SyntheticDataGenerator(
    config=config,
    num_customers=5000,
    num_products=500,
    num_orders=50000,
    seed=42
)

# Generate
data = generator.generate_and_save_all()
generator.get_data_summary(
    data['customers'],
    data['products'],
    data['orders']
)

# Analyze
customers = data['customers']
products = data['products']
orders = data['orders']

print(f"Total customers: {len(customers):,}")
print(f"Total products: {len(products):,}")
print(f"Total orders: {len(orders):,}")

# Pareto check
orders_per_cust = orders.groupby('customer_id').size()
top_20 = orders_per_cust.nlargest(int(len(customers)*0.2)).sum()
print(f"Top 20%: {top_20/len(orders)*100:.1f}%")

# Product stats
print(f"Avg rating: {products['rating'].mean():.2f}")
print(f"Price range: ${products['price'].min():.2f}-${products['price'].max():.2f}")
```

## Documentation Links
- **SYNTHETIC_DATA_GUIDE.md** - Comprehensive guide
- **QUICK_START_EXAMPLES.py** - Working examples
- **demo_synthetic_data.py** - Interactive demo
- **IMPLEMENTATION_SUMMARY.md** - Technical details

## Key Methods
```python
generate_customers()                     # → DataFrame
generate_products()                      # → DataFrame
generate_orders_with_pareto(df_c, df_p) # → DataFrame
save_data(df, filename)                 # → Path
generate_and_save_all()                 # → Dict[str, DataFrame]
get_data_summary(df_c, df_p, df_o)      # → None (prints)
```

## Constants
```python
CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home",
    "Sports",
    "Books"
]

PRICE_RANGES = {
    "Electronics": (50, 500),
    "Clothing": (10, 150),
    "Home": (20, 300),
    "Sports": (15, 250),
    "Books": (8, 50),
}
```

---
**Quick Reference v1.0** | Keep handy while developing!
