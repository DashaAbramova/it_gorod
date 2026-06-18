-- 1. STAGING TABLES (Таблицы для сырых данных)

-- Таблица для сырых данных клиентов
CREATE TABLE IF NOT EXISTS stg_customers (
    customer_id VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    registration_date TIMESTAMP,
    customer_segment VARCHAR(50),
    email_valid BOOLEAN
);

COMMENT ON TABLE stg_customers IS 'Сырые данные клиентов из CSV';
COMMENT ON COLUMN stg_customers.customer_id IS 'Уникальный идентификатор клиента';
COMMENT ON COLUMN stg_customers.email_valid IS 'Флаг корректности email (после валидации)';

-- Таблица для сырых данных заказов
CREATE TABLE IF NOT EXISTS stg_orders (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    order_date TIMESTAMP,
    order_status VARCHAR(30),
    payment_id VARCHAR(50)
);

COMMENT ON TABLE stg_orders IS 'Сырые данные заказов из JSON';

-- Таблица для сырых данных товаров
CREATE TABLE IF NOT EXISTS stg_products (
    product_id VARCHAR(50),
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    price DECIMAL(10,2),
    cost DECIMAL(10,2)
);

COMMENT ON TABLE stg_products IS 'Сырые данные товаров из XLSX';

-- Таблица для сырых данных событий
CREATE TABLE IF NOT EXISTS stg_events (
    event_id VARCHAR(50),
    user_id VARCHAR(50),
    event_date TIMESTAMP,
    event_type VARCHAR(50),
    event_category VARCHAR(50),
    page_visited VARCHAR(200),
    duration_seconds INTEGER,
    device_type VARCHAR(30),
    browser VARCHAR(30)
);

COMMENT ON TABLE stg_events IS 'Сырые данные событий из XML';

-- Таблица для сырых данных платежей
CREATE TABLE IF NOT EXISTS stg_payments (
    payment_id VARCHAR(50),
    order_id VARCHAR(50),
    payment_method VARCHAR(50),
    amount DECIMAL(10,2),
    payment_date TIMESTAMP,
    status VARCHAR(30)
);

COMMENT ON TABLE stg_payments IS 'Сырые данные платежей из CSV';

-- 2. DIMENSION TABLES (Таблицы измерений)

-- Измерение: Клиенты
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_sk SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(200),
    email VARCHAR(100),
    phone VARCHAR(20),
    registration_date DATE,
    customer_segment VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dim_customer IS 'Измерение: Информация о клиентах';
COMMENT ON COLUMN dim_customer.customer_sk IS 'Суррогатный ключ';
COMMENT ON COLUMN dim_customer.customer_id IS 'Бизнес-ключ из источника';

-- Измерение: Товары
CREATE TABLE IF NOT EXISTS dim_product (
    product_sk SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    price DECIMAL(10,2),
    cost DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dim_product IS 'Измерение: Информация о товарах';

-- Измерение: Даты
CREATE TABLE IF NOT EXISTS dim_date (
    date_sk SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    week INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    is_weekend BOOLEAN DEFAULT FALSE,
    is_holiday BOOLEAN DEFAULT FALSE
);

COMMENT ON TABLE dim_date IS 'Измерение: Календарь дат';

-- Измерение: Платежи
CREATE TABLE IF NOT EXISTS dim_payment (
    payment_sk SERIAL PRIMARY KEY,
    payment_id VARCHAR(50) UNIQUE NOT NULL,
    payment_method VARCHAR(50),
    payment_status VARCHAR(30),
    payment_type VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dim_payment IS 'Измерение: Информация о платежах';

-- 3. FACT TABLES (Таблицы фактов)

-- Факт: Заказы
CREATE TABLE IF NOT EXISTS fact_orders (
    order_sk SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    customer_sk INTEGER REFERENCES dim_customer(customer_sk),
    product_sk INTEGER REFERENCES dim_product(product_sk),
    date_sk INTEGER REFERENCES dim_date(date_sk),
    payment_sk INTEGER REFERENCES dim_payment(payment_sk),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    order_status VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE fact_orders IS 'Факт: Данные о заказах';

-- Факт: События
CREATE TABLE IF NOT EXISTS fact_events (
    event_sk SERIAL PRIMARY KEY,
    event_id VARCHAR(50) UNIQUE NOT NULL,
    customer_sk INTEGER REFERENCES dim_customer(customer_sk),
    date_sk INTEGER REFERENCES dim_date(date_sk),
    event_type VARCHAR(50),
    event_category VARCHAR(50),
    page_visited VARCHAR(200),
    duration_seconds INTEGER,
    device_type VARCHAR(30),
    browser VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE fact_events IS 'Факт: Данные о событиях пользователей';

-- 4. ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ

-- Индексы для fact_orders
CREATE INDEX IF NOT EXISTS idx_fact_orders_customer ON fact_orders(customer_sk);
CREATE INDEX IF NOT EXISTS idx_fact_orders_product ON fact_orders(product_sk);
CREATE INDEX IF NOT EXISTS idx_fact_orders_date ON fact_orders(date_sk);
CREATE INDEX IF NOT EXISTS idx_fact_orders_payment ON fact_orders(payment_sk);
CREATE INDEX IF NOT EXISTS idx_fact_orders_order_id ON fact_orders(order_id);
CREATE INDEX IF NOT EXISTS idx_fact_orders_status ON fact_orders(order_status);

-- Индексы для fact_events
CREATE INDEX IF NOT EXISTS idx_fact_events_customer ON fact_events(customer_sk);
CREATE INDEX IF NOT EXISTS idx_fact_events_date ON fact_events(date_sk);
CREATE INDEX IF NOT EXISTS idx_fact_events_event_type ON fact_events(event_type);
CREATE INDEX IF NOT EXISTS idx_fact_events_event_id ON fact_events(event_id);

-- Индексы для измерений
CREATE INDEX IF NOT EXISTS idx_dim_customer_email ON dim_customer(email);
CREATE INDEX IF NOT EXISTS idx_dim_customer_segment ON dim_customer(customer_segment);
CREATE INDEX IF NOT EXISTS idx_dim_product_category ON dim_product(category);
CREATE INDEX IF NOT EXISTS idx_dim_date_year_month ON dim_date(year, month);
CREATE INDEX IF NOT EXISTS idx_dim_payment_method ON dim_payment(payment_method);

-- 5. ПРЕДСТАВЛЕНИЯ ДЛЯ АНАЛИТИКИ

-- Представление: Топ клиентов
CREATE OR REPLACE VIEW v_top_customers AS
SELECT 
    c.customer_name,
    c.email,
    COUNT(DISTINCT f.order_id) as total_orders,
    SUM(f.total_amount) as total_spent,
    ROUND(AVG(f.total_amount), 2) as avg_order_value
FROM fact_orders f
JOIN dim_customer c ON f.customer_sk = c.customer_sk
GROUP BY c.customer_sk, c.customer_name, c.email
ORDER BY total_spent DESC;

-- Представление: Ежемесячная выручка
CREATE OR REPLACE VIEW v_monthly_revenue AS
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

-- Представление: Популярные товары
CREATE OR REPLACE VIEW v_popular_products AS
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
ORDER BY total_quantity_sold DESC;

-- Представление: Активность клиентов
CREATE OR REPLACE VIEW v_customer_activity AS
SELECT 
    c.customer_name,
    c.email,
    COUNT(DISTINCT f.order_id) as order_count,
    SUM(f.total_amount) as total_spent,
    MAX(d.date) as last_activity,
    MIN(d.date) as first_activity
FROM dim_customer c
LEFT JOIN fact_orders f ON c.customer_sk = f.customer_sk
LEFT JOIN dim_date d ON f.date_sk = d.date_sk
GROUP BY c.customer_sk, c.customer_name, c.email;

-- 6. ТРИГГЕРЫ ДЛЯ АВТООБНОВЛЕНИЯ

-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для dim_customer
DROP TRIGGER IF EXISTS update_customer_updated_at ON dim_customer;
CREATE TRIGGER update_customer_updated_at
    BEFORE UPDATE ON dim_customer
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Триггер для dim_product
DROP TRIGGER IF EXISTS update_product_updated_at ON dim_product;
CREATE TRIGGER update_product_updated_at
    BEFORE UPDATE ON dim_product
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 7. ПРОВЕРОЧНЫЕ ЗАПРОСЫ

-- Проверка: Заказы без клиентов
CREATE OR REPLACE VIEW v_orphan_orders AS
SELECT f.*
FROM fact_orders f
LEFT JOIN dim_customer c ON f.customer_sk = c.customer_sk
WHERE c.customer_sk IS NULL;

-- Проверка: Заказы без товаров
CREATE OR REPLACE VIEW v_orphan_products AS
SELECT f.*
FROM fact_orders f
LEFT JOIN dim_product p ON f.product_sk = p.product_sk
WHERE p.product_sk IS NULL;

-- Проверка: Статистика по таблицам
CREATE OR REPLACE VIEW v_table_stats AS
SELECT 
    'fact_orders' as table_name,
    COUNT(*) as row_count,
    COUNT(DISTINCT customer_sk) as unique_customers
FROM fact_orders
UNION ALL
SELECT 
    'fact_events' as table_name,
    COUNT(*) as row_count,
    COUNT(DISTINCT customer_sk) as unique_customers
FROM fact_events;

-- 8. ОЧИСТКА СТАРЫХ ДАННЫХ

-- Функция для очистки старых событий
CREATE OR REPLACE FUNCTION clean_old_events(days_to_keep INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM fact_events 
    WHERE date_sk IN (
        SELECT date_sk FROM dim_date 
        WHERE date < CURRENT_DATE - days_to_keep * INTERVAL '1 day'
    );
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ language 'plpgsql';

-- 9. КОНТРОЛЬНЫЕ СУММЫ (для проверки целостности)

-- Функция проверки целостности данных
CREATE OR REPLACE FUNCTION check_data_integrity()
RETURNS TABLE(
    check_name VARCHAR(100),
    status VARCHAR(20),
    details TEXT
) AS $$
BEGIN
    -- Проверка 1: Все заказы имеют клиента
    RETURN QUERY
    SELECT 
        'Orders without customers'::VARCHAR,
        CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'FAIL' END,
        COUNT(*)::TEXT || ' orphan orders found'
    FROM fact_orders f
    LEFT JOIN dim_customer c ON f.customer_sk = c.customer_sk
    WHERE c.customer_sk IS NULL;
    
    -- Проверка 2: Все заказы имеют товар
    RETURN QUERY
    SELECT 
        'Orders without products'::VARCHAR,
        CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'FAIL' END,
        COUNT(*)::TEXT || ' orphan orders found'
    FROM fact_orders f
    LEFT JOIN dim_product p ON f.product_sk = p.product_sk
    WHERE p.product_sk IS NULL;
END;
$$ language 'plpgsql';

-- 10. ОПТИМИЗАЦИЯ (обновление статистики)

-- Обновление статистики для всех таблиц
ANALYZE fact_orders;
ANALYZE fact_events;
ANALYZE dim_customer;
ANALYZE dim_product;
ANALYZE dim_date;
ANALYZE dim_payment;

-- 11. ИНФОРМАЦИЯ О СХЕМЕ

-- Вывод информации о всех таблицах
SELECT 
    schemaname,
    tablename,
    tableowner,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
