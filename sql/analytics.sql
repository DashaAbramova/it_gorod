-- 1. Топ-10 клиентов по сумме покупок
SELECT 
    c.customer_name,
    c.email,
    COUNT(DISTINCT f.order_id) as total_orders,
    SUM(f.total_amount) as total_purchase_amount,
    ROUND(AVG(f.total_amount), 2) as avg_order_value
FROM fact_orders f
JOIN dim_customer c ON f.customer_sk = c.customer_sk
GROUP BY c.customer_sk, c.customer_name, c.email
ORDER BY total_purchase_amount DESC
LIMIT 10;

-- 2. Выручка по месяцам
SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id) as order_count,
    SUM(f.total_amount) as revenue,
    ROUND(AVG(f.total_amount), 2) as avg_order_value,
    COUNT(DISTINCT f.customer_sk) as unique_customers
FROM fact_orders f
JOIN dim_date d ON f.date_sk = d.date_sk
GROUP BY d.year, d.month, d.month_name, d.month
ORDER BY d.year DESC, d.month DESC;

-- 3. Самые популярные товары
SELECT 
    p.product_name,
    p.category,
    COUNT(DISTINCT f.order_id) as order_count,
    SUM(f.quantity) as total_quantity_sold,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.unit_price), 2) as avg_unit_price
FROM fact_orders f
JOIN dim_product p ON f.product_sk = p.product_sk
GROUP BY p.product_sk, p.product_name, p.category
ORDER BY total_quantity_sold DESC
LIMIT 10;

-- 4. Последняя активность топ-5 пользователей с наибольшим количеством покупок
WITH customer_purchases AS (
    SELECT 
        c.customer_sk,
        c.customer_name,
        c.email,
        COUNT(DISTINCT f.order_id) as order_count,
        MAX(d.date) as last_activity_date,
        SUM(f.total_amount) as total_spent
    FROM fact_orders f
    JOIN dim_customer c ON f.customer_sk = c.customer_sk
    JOIN dim_date d ON f.date_sk = d.date_sk
    GROUP BY c.customer_sk, c.customer_name, c.email
)
SELECT 
    customer_name,
    email,
    order_count,
    total_spent,
    last_activity_date,
    RANK() OVER (ORDER BY order_count DESC) as purchase_rank
FROM customer_purchases
ORDER BY order_count DESC
LIMIT 5;

-- 5. Пользователи без заказов
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    c.registration_date,
    c.customer_segment
FROM dim_customer c
LEFT JOIN fact_orders f ON c.customer_sk = f.customer_sk
WHERE f.order_sk IS NULL
ORDER BY c.registration_date DESC;

-- Дополнительные аналитические запросы

-- 6. Распределение заказов по статусам
SELECT 
    order_status,
    COUNT(*) as order_count,
    SUM(total_amount) as total_amount,
    ROUND(AVG(total_amount), 2) as avg_amount
FROM fact_orders
GROUP BY order_status
ORDER BY order_count DESC;

-- 7. Анализ платежей по методам
SELECT 
    dp.payment_method,
    COUNT(*) as payment_count,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_payment_amount,
    COUNT(DISTINCT f.customer_sk) as unique_customers
FROM fact_orders f
JOIN dim_payment dp ON f.payment_sk = dp.payment_sk
GROUP BY dp.payment_method
ORDER BY total_revenue DESC;

-- 8. Анализ поведения пользователей (события)
SELECT 
    e.event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT e.customer_sk) as unique_users,
    ROUND(AVG(e.duration_seconds), 0) as avg_duration_seconds,
    COUNT(DISTINCT DATE(e.date_sk)) as active_days
FROM fact_events e
GROUP BY e.event_type
ORDER BY event_count DESC;

-- 9. Продукты, приносящие наибольшую маржинальность
SELECT 
    p.product_name,
    p.category,
    SUM(f.total_amount) as revenue,
    SUM(f.quantity * p.cost) as total_cost,
    SUM(f.total_amount) - SUM(f.quantity * p.cost) as total_margin,
    ROUND(((SUM(f.total_amount) - SUM(f.quantity * p.cost)) / NULLIF(SUM(f.total_amount), 0) * 100), 2) as margin_percentage
FROM fact_orders f
JOIN dim_product p ON f.product_sk = p.product_sk
WHERE p.cost > 0
GROUP BY p.product_sk, p.product_name, p.category
HAVING SUM(f.total_amount) > 0
ORDER BY total_margin DESC
LIMIT 10;

-- 10. Сегментация клиентов по активности
WITH customer_metrics AS (
    SELECT 
        c.customer_sk,
        c.customer_name,
        c.customer_segment,
        COUNT(DISTINCT f.order_id) as order_count,
        SUM(f.total_amount) as total_spent,
        MAX(d.date) as last_order_date,
        MIN(d.date) as first_order_date,
        COUNT(DISTINCT d.date) as active_days
    FROM dim_customer c
    LEFT JOIN fact_orders f ON c.customer_sk = f.customer_sk
    LEFT JOIN dim_date d ON f.date_sk = d.date_sk
    GROUP BY c.customer_sk, c.customer_name, c.customer_segment
)
SELECT 
    customer_segment,
    COUNT(*) as customers_count,
    ROUND(AVG(order_count), 2) as avg_orders,
    ROUND(AVG(total_spent), 2) as avg_spent,
    ROUND(AVG(active_days), 2) as avg_active_days,
    ROUND(AVG(total_spent / NULLIF(order_count, 0)), 2) as avg_order_value
FROM customer_metrics
GROUP BY customer_segment
ORDER BY avg_spent DESC;
