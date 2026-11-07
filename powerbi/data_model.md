# Power BI model
FactOrderItems: one row per order line with order_id, menu_item_id, quantity, unit_price and estimated_unit_cost. FactOrders: one row per order with customer, timestamp, channel and status. Dimensions: DimMenu, DimCustomer and DimDate.

Count order IDs distinctly for order KPIs. Calculate revenue from line items filtered to completed orders. Avoid summing order-level amounts after joining to multiple order lines.

Pages: (1) Executive sales—gross sales, completed orders, AOV, monthly revenue. (2) Menu engineering—category/item revenue, units, estimated contribution. (3) Demand—weekday/hour matrix and channel mix. (4) Customers—repeat share and frequency. (5) Inventory—requires a real stock-movement ledger.

Costs are illustrative; taxes, discounts, refunds, recipe-level usage, labor and waste are not modeled.
