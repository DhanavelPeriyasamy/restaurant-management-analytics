-- MySQL 8+ | Tables: orders, order_items, menu, customers
-- Sales and AOV; count orders distinctly to avoid line-item fan-out
SELECT COUNT(DISTINCT o.order_id) completed_orders,ROUND(SUM(i.quantity*i.unit_price),2) gross_sales,
ROUND(SUM(i.quantity*i.unit_price)/COUNT(DISTINCT o.order_id),2) average_order_value
FROM orders o JOIN order_items i USING(order_id) WHERE o.order_status='Completed';

-- Menu mix and estimated contribution
SELECT m.item_name,m.category,SUM(i.quantity) units_sold,
ROUND(SUM(i.quantity*i.unit_price),2) revenue,
ROUND(SUM(i.quantity*(i.unit_price-i.estimated_unit_cost)),2) estimated_contribution
FROM order_items i JOIN menu m USING(menu_item_id) JOIN orders o USING(order_id)
WHERE o.order_status='Completed' GROUP BY m.menu_item_id,m.item_name,m.category ORDER BY revenue DESC;

-- Weekday and hour demand
SELECT DAYNAME(order_datetime) weekday_name,HOUR(order_datetime) order_hour,COUNT(*) completed_orders
FROM orders WHERE order_status='Completed' GROUP BY weekday_name,order_hour ORDER BY completed_orders DESC;

-- Repeat customers
WITH x AS (SELECT customer_id,COUNT(DISTINCT order_id) order_count FROM orders
WHERE order_status='Completed' GROUP BY customer_id)
SELECT CASE WHEN order_count>=2 THEN 'Repeat' ELSE 'One-time' END customer_type,COUNT(*) customers
FROM x GROUP BY customer_type;

-- Monthly sales trend
SELECT DATE_FORMAT(o.order_datetime,'%Y-%m') sales_month,COUNT(DISTINCT o.order_id) orders,
ROUND(SUM(i.quantity*i.unit_price),2) revenue
FROM orders o JOIN order_items i USING(order_id) WHERE o.order_status='Completed'
GROUP BY sales_month ORDER BY sales_month;

-- Top customer cohort using ranking
WITH spend AS (SELECT o.customer_id,SUM(i.quantity*i.unit_price) lifetime_sales
FROM orders o JOIN order_items i USING(order_id) WHERE o.order_status='Completed' GROUP BY o.customer_id),
ranked AS (SELECT *,DENSE_RANK() OVER(ORDER BY lifetime_sales DESC) spend_rank FROM spend)
SELECT * FROM ranked WHERE spend_rank<=20 ORDER BY spend_rank;
