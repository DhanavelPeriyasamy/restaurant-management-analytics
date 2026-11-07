# Restaurant Business & Revenue Intelligence

An end-to-end restaurant analytics portfolio project covering sales performance, menu mix, customer behavior, and inventory movement. It provides synthetic transactional data, Python summaries, MySQL analytics queries, and a Power BI dashboard blueprint.

> **Data note:** Data is synthetic and generated for demonstration. It does not represent a real restaurant, customer, supplier, or financial result.

## Business questions
- What are revenue, order volume, average order value, and sales trends?
- Which menu items and categories contribute most to revenue?
- When are peak ordering periods?
- Which customers drive repeat visits?
- How do inventory movements compare with sales demand?

## KPI definitions
| KPI | Definition |
|---|---|
| Gross sales | Sum of line-item quantity × unit price |
| Orders | Distinct order count |
| Average order value | Gross sales / distinct orders |
| Item mix % | Item revenue / total revenue |
| Repeat customer rate | Customers with 2+ orders / customers with an order |
| Estimated gross margin | (Sales − estimated ingredient cost) / sales |

Margin is illustrative because recipe costing, waste, tax, discounts, and labor are simplified in this demo.

## Structure
```text
├── README.md
├── requirements.txt
├── data/                       # generated CSVs (ignored)
├── src/
│   ├── generate_data.py
│   └── analyze_sales.py
├── sql/
│   └── restaurant_analytics.sql
├── powerbi/
│   ├── data_model.md
│   └── dax_measures.dax
└── docs/
    └── business_questions.md
```

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/generate_data.py
python src/analyze_sales.py
```

## Dashboard pages
1. **Executive sales:** revenue, orders, average order value, trend.
2. **Menu engineering:** item/category sales, contribution, estimated margin.
3. **Demand patterns:** weekday and hour heatmap, peak order windows.
4. **Customer insights:** new vs repeat customers, order frequency.
5. **Inventory:** item-level movement and replenishment watchlist.

## Technical notes
- Order-level and line-item-level facts are separate to avoid double-counting.
- Use order_id as the grain for order KPIs and order_item_id for line-item analysis.
- Validate joins and aggregation grain before calculating revenue.
- Do not treat estimated ingredient costs as audited profitability.

## Skills demonstrated
Python/Pandas, synthetic data generation, relational schema design, SQL joins/CTEs/window functions, revenue and product-mix analysis, Power BI modeling, DAX, and business recommendations.

## Author
**Dhanavel Periyasamy** · Data Analytics Portfolio
