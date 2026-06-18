from sqlalchemy import create_engine, text
from loguru import logger
from src.config import Config

class DWHBuilder:
    def __init__(self):
        self.engine = create_engine(Config.get_db_url())
    
    def create_dwh_schema(self):
        logger.info("=" * 50)
        logger.info("Creating DWH schema...")
        logger.info("=" * 50)
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                DROP TABLE IF EXISTS fact_orders CASCADE;
                DROP TABLE IF EXISTS fact_events CASCADE;
                DROP TABLE IF EXISTS dim_customer CASCADE;
                DROP TABLE IF EXISTS dim_product CASCADE;
                DROP TABLE IF EXISTS dim_date CASCADE;
                DROP TABLE IF EXISTS dim_payment CASCADE;
                DROP TABLE IF EXISTS stg_customers CASCADE;
                DROP TABLE IF EXISTS stg_orders CASCADE;
                DROP TABLE IF EXISTS stg_products CASCADE;
                DROP TABLE IF EXISTS stg_events CASCADE;
                DROP TABLE IF EXISTS stg_payments CASCADE;
            """))
            conn.commit()
            
            conn.execute(text("""
                CREATE TABLE stg_customers (
                    customer_id VARCHAR(50),
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    registration_date TIMESTAMP,
                    customer_segment VARCHAR(50),
                    email_valid BOOLEAN
                );
                
                CREATE TABLE stg_orders (
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
                
                CREATE TABLE stg_products (
                    product_id VARCHAR(50),
                    product_name VARCHAR(200),
                    category VARCHAR(100),
                    subcategory VARCHAR(100),
                    price DECIMAL(10,2),
                    cost DECIMAL(10,2)
                );
                
                CREATE TABLE stg_events (
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
                
                CREATE TABLE stg_payments (
                    payment_id VARCHAR(50),
                    order_id VARCHAR(50),
                    payment_method VARCHAR(50),
                    amount DECIMAL(10,2),
                    payment_date TIMESTAMP,
                    status VARCHAR(30)
                );
            """))
            conn.commit()
            
            # Create dimension tables
            conn.execute(text("""
                -- Customer dimension
                CREATE TABLE dim_customer (
                    customer_sk SERIAL PRIMARY KEY,
                    customer_id VARCHAR(50) UNIQUE,
                    customer_name VARCHAR(200),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    registration_date DATE,
                    customer_segment VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Product dimension
                CREATE TABLE dim_product (
                    product_sk SERIAL PRIMARY KEY,
                    product_id VARCHAR(50) UNIQUE,
                    product_name VARCHAR(200),
                    category VARCHAR(100),
                    subcategory VARCHAR(100),
                    price DECIMAL(10,2),
                    cost DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Date dimension
                CREATE TABLE dim_date (
                    date_sk SERIAL PRIMARY KEY,
                    date DATE UNIQUE,
                    year INTEGER,
                    quarter INTEGER,
                    month INTEGER,
                    month_name VARCHAR(20),
                    week INTEGER,
                    day_of_week INTEGER,
                    day_name VARCHAR(20),
                    is_weekend BOOLEAN,
                    is_holiday BOOLEAN DEFAULT FALSE
                );
                
                -- Payment dimension
                CREATE TABLE dim_payment (
                    payment_sk SERIAL PRIMARY KEY,
                    payment_id VARCHAR(50) UNIQUE,
                    payment_method VARCHAR(50),
                    payment_status VARCHAR(30),
                    payment_type VARCHAR(30),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Fact orders
                CREATE TABLE fact_orders (
                    order_sk SERIAL PRIMARY KEY,
                    order_id VARCHAR(50) UNIQUE,
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
                
                -- Fact events
                CREATE TABLE fact_events (
                    event_sk SERIAL PRIMARY KEY,
                    event_id VARCHAR(50) UNIQUE,
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
                
                -- Create indexes for performance
                CREATE INDEX idx_fact_orders_customer ON fact_orders(customer_sk);
                CREATE INDEX idx_fact_orders_date ON fact_orders(date_sk);
                CREATE INDEX idx_fact_orders_product ON fact_orders(product_sk);
                CREATE INDEX idx_fact_events_customer ON fact_events(customer_sk);
                CREATE INDEX idx_fact_events_date ON fact_events(date_sk);
                CREATE INDEX idx_dim_customer_email ON dim_customer(email);
                CREATE INDEX idx_dim_product_category ON dim_product(category);
                CREATE INDEX idx_fact_orders_order_id ON fact_orders(order_id);
            """))
            conn.commit()
            logger.info("✅ DWH schema created successfully")
    
    def populate_dimensions(self):
        logger.info("Populating dimension tables...")
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO dim_customer (customer_id, customer_name, email, phone, registration_date, customer_segment)
                SELECT 
                    customer_id,
                    CONCAT(first_name, ' ', last_name) as customer_name,
                    email,
                    phone,
                    registration_date::date,
                    customer_segment
                FROM stg_customers
                WHERE customer_id IS NOT NULL
                ON CONFLICT (customer_id) DO UPDATE SET
                    customer_name = EXCLUDED.customer_name,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    registration_date = EXCLUDED.registration_date,
                    customer_segment = EXCLUDED.customer_segment,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING customer_id
            """))
            logger.info(f"✅ Populated dim_customer with {result.rowcount} records")
            
            result = conn.execute(text("""
                INSERT INTO dim_product (product_id, product_name, category, subcategory, price, cost)
                SELECT 
                    product_id,
                    product_name,
                    category,
                    subcategory,
                    price,
                    cost
                FROM stg_products
                WHERE product_id IS NOT NULL
                ON CONFLICT (product_id) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    category = EXCLUDED.category,
                    subcategory = EXCLUDED.subcategory,
                    price = EXCLUDED.price,
                    cost = EXCLUDED.cost,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING product_id
            """))
            logger.info(f"✅ Populated dim_product with {result.rowcount} records")
            
            result = conn.execute(text("""
                INSERT INTO dim_date (date, year, quarter, month, month_name, 
                                    week, day_of_week, day_name, is_weekend)
                SELECT DISTINCT
                    order_date::date as date,
                    EXTRACT(YEAR FROM order_date)::integer as year,
                    EXTRACT(QUARTER FROM order_date)::integer as quarter,
                    EXTRACT(MONTH FROM order_date)::integer as month,
                    TO_CHAR(order_date, 'Month') as month_name,
                    EXTRACT(WEEK FROM order_date)::integer as week,
                    EXTRACT(DOW FROM order_date)::integer as day_of_week,
                    TO_CHAR(order_date, 'Day') as day_name,
                    CASE WHEN EXTRACT(DOW FROM order_date) IN (0, 6) THEN TRUE ELSE FALSE END as is_weekend
                FROM stg_orders
                WHERE order_date IS NOT NULL
                ON CONFLICT (date) DO NOTHING
            """))
            logger.info(f"✅ Populated dim_date with {result.rowcount} records")
            
            result = conn.execute(text("""
                INSERT INTO dim_payment (payment_id, payment_method, payment_status)
                SELECT 
                    payment_id,
                    payment_method,
                    status as payment_status
                FROM stg_payments
                WHERE payment_id IS NOT NULL
                ON CONFLICT (payment_id) DO UPDATE SET
                    payment_method = EXCLUDED.payment_method,
                    payment_status = EXCLUDED.payment_status
                RETURNING payment_id
            """))
            logger.info(f"✅ Populated dim_payment with {result.rowcount} records")
            
            conn.commit()
    
    def populate_facts(self):
        logger.info("Populating fact tables...")
        
        with self.engine.connect() as conn:
            # Populate fact orders
            result = conn.execute(text("""
                INSERT INTO fact_orders (
                    order_id, customer_sk, product_sk, date_sk, 
                    payment_sk, quantity, unit_price, total_amount, order_status
                )
                SELECT 
                    o.order_id,
                    dc.customer_sk,
                    dp.product_sk,
                    dd.date_sk,
                    dpmt.payment_sk,
                    o.quantity,
                    o.unit_price,
                    o.total_amount,
                    o.order_status
                FROM stg_orders o
                LEFT JOIN dim_customer dc ON o.customer_id = dc.customer_id
                LEFT JOIN dim_product dp ON o.product_id = dp.product_id
                LEFT JOIN dim_date dd ON o.order_date::date = dd.date
                LEFT JOIN dim_payment dpmt ON o.payment_id = dpmt.payment_id
                WHERE o.order_id IS NOT NULL
                ON CONFLICT (order_id) DO UPDATE SET
                    customer_sk = EXCLUDED.customer_sk,
                    product_sk = EXCLUDED.product_sk,
                    date_sk = EXCLUDED.date_sk,
                    payment_sk = EXCLUDED.payment_sk,
                    quantity = EXCLUDED.quantity,
                    unit_price = EXCLUDED.unit_price,
                    total_amount = EXCLUDED.total_amount,
                    order_status = EXCLUDED.order_status
                RETURNING order_id
            """))
            logger.info(f"✅ Populated fact_orders with {result.rowcount} records")
            
            result = conn.execute(text("""
                INSERT INTO fact_events (
                    event_id, customer_sk, date_sk, event_type,
                    event_category, page_visited, duration_seconds, device_type, browser
                )
                SELECT 
                    e.event_id,
                    dc.customer_sk,
                    dd.date_sk,
                    e.event_type,
                    e.event_category,
                    e.page_visited,
                    e.duration_seconds,
                    e.device_type,
                    e.browser
                FROM stg_events e
                LEFT JOIN dim_customer dc ON e.user_id = dc.customer_id
                LEFT JOIN dim_date dd ON e.event_date::date = dd.date
                WHERE e.event_id IS NOT NULL
                ON CONFLICT (event_id) DO UPDATE SET
                    customer_sk = EXCLUDED.customer_sk,
                    date_sk = EXCLUDED.date_sk,
                    event_type = EXCLUDED.event_type,
                    event_category = EXCLUDED.event_category,
                    page_visited = EXCLUDED.page_visited,
                    duration_seconds = EXCLUDED.duration_seconds,
                    device_type = EXCLUDED.device_type,
                    browser = EXCLUDED.browser
                RETURNING event_id
            """))
            logger.info(f"✅ Populated fact_events with {result.rowcount} records")
            
            conn.commit()
    
    def build(self):
        logger.info("=" * 50)
        logger.info("🏗️ Starting DWH build...")
        logger.info("=" * 50)
        
        try:
            self.create_dwh_schema()
            self.populate_dimensions()
            self.populate_facts()
            
            logger.info("=" * 50)
            logger.info("✅ DWH build completed successfully!")
            logger.info("=" * 50)
            return True
        except Exception as e:
            logger.error(f"❌ DWH build failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
