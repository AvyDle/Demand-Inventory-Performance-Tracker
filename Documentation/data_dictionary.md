# S&OP Data Dictionary

## Orders Dataset
- **order_id**: Unique identifier for each order
- **product_id**: Product SKU identifier
- **order_date**: Date when the order was placed
- **qty**: Quantity of products ordered
- **order_value**: Total monetary value of the order
- **region**: Geographic region where order was placed
- **customer_type**: Customer segment (Business, Individual, Premium)
- **base_price**: Original product price before discounts
- **unit_price**: Final price per unit after discounts
- **discount_pct**: Percentage discount applied
- **order_month**: Month of order for aggregation purposes
- **category**: Product category classification
- **is_on_sale**: Boolean indicating if product was on sale
- **sale_event**: Type of sales event (if applicable)
- **day_of_week**: Day of the week when order was placed

## Products Dataset
- **product_id**: Unique product SKU identifier
- **product_name**: Full product name and description
- **category**: Product category (Electronics, Kitchen & Dining, etc.)
- **base_price**: Standard retail price
- **sales_events_count**: Number of sales events product participated in
- **promotional_tier**: Promotional classification (High, Medium, Low)
- **demand_volatility**: Demand variability classification (High, Medium, Low)

## Inventory Dataset
- **product_id**: Product SKU identifier
- **available_qty**: Current available stock quantity
- **warehouse**: Warehouse location identifier
- **stock_status**: Current stock status (Excess, Adequate, Low)
- **unit_cost**: Cost per unit for inventory valuation
- **inventory_value**: Total value of available inventory
- **total_demand**: Total historical demand for the product

## Forecasts Dataset
- **product_id**: Product SKU identifier
- **forecast_month**: Month for which forecast is made
- **forecast_qty**: Predicted demand quantity
- **actual_demand**: Actual observed demand
- **variance_pct**: Percentage difference between forecast and actual
- **forecast_type**: Method used (Manual, Statistical, ML_Model)
- **confidence_level**: Confidence in forecast (High, Medium, Low)

## Data Quality Standards
- All datasets undergo validation for completeness and accuracy
- Missing values are handled through appropriate imputation methods
- Data consistency is maintained across all related tables
- Regular audits ensure data integrity and reliability
