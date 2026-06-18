import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from src.config import Config
from src.utils import (
    read_csv, read_json, read_xlsx, read_xml, 
    clean_date, clean_currency, validate_email
)
from src.data_quality import DataQualityChecker
import os

class ETLPipeline:
    def __init__(self):
        self.engine = create_engine(Config.get_db_url())
        self.dq_checker = DataQualityChecker()
        self.loaded_data = {}
        self.rejected_records = []
    
    def extract(self):
        logger.info("=" * 50)
        logger.info("Starting EXTRACTION process...")
        logger.info("=" * 50)

        customers_path = os.path.join(Config.DATA_PATH, 'customers.csv')
        self.loaded_data['customers'] = read_csv(customers_path)
        logger.info(f"Extracted {len(self.loaded_data['customers'])} customers")
        
        orders_path = os.path.join(Config.DATA_PATH, 'orders.json')
        self.loaded_data['orders'] = read_json(orders_path)
        logger.info(f"Extracted {len(self.loaded_data['orders'])} orders")
        
        products_path = os.path.join(Config.DATA_PATH, 'products.xlsx')
        self.loaded_data['products'] = read_xlsx(products_path)
        logger.info(f"Extracted {len(self.loaded_data['products'])} products")
        
        events_path = os.path.join(Config.DATA_PATH, 'events.xml')
        self.loaded_data['events'] = read_xml(events_path)
        logger.info(f"Extracted {len(self.loaded_data['events'])} events")
        
        payments_path = os.path.join(Config.DATA_PATH, 'payments.csv')
        self.loaded_data['payments'] = read_csv(payments_path)
        logger.info(f"Extracted {len(self.loaded_data['payments'])} payments")
        
        logger.info("✅ Extraction completed successfully")
        return self.loaded_data
    
    def transform(self):
        logger.info("=" * 50)
        logger.info("Starting TRANSFORMATION process...")
        logger.info("=" * 50)
        
        if not self.loaded_data['customers'].empty:
            logger.info("Processing customers...")
            df = self.loaded_data['customers'].copy()
            
            if 'registration_date' in df.columns:
                df['registration_date'] = df['registration_date'].apply(clean_date)
            
            if 'email' in df.columns:
                df['email_valid'] = df['email'].apply(validate_email)
                invalid_emails = df[~df['email_valid']]
                if not invalid_emails.empty:
                    logger.warning(f"Found {len(invalid_emails)} invalid emails")
            
            self.dq_checker.clear()
            self.dq_checker.check_missing_values(df, ['customer_id', 'email'])
            self.dq_checker.check_duplicates(df, ['customer_id'])
            self.dq_checker.log_issues('customers')
            self.rejected_records.extend(self.dq_checker.get_rejected_records())
            
            self.loaded_data['customers'] = df
            logger.info(f"✅ Processed {len(df)} customers")
        
        if not self.loaded_data['orders'].empty:
            logger.info("Processing orders...")
            df = self.loaded_data['orders'].copy()
            
            if 'order_date' in df.columns:
                df['order_date'] = df['order_date'].apply(clean_date)
            if 'total_amount' in df.columns:
                df['total_amount'] = df['total_amount'].apply(clean_currency)
            if 'unit_price' in df.columns:
                df['unit_price'] = df['unit_price'].apply(clean_currency)
            
            self.dq_checker.clear()
            self.dq_checker.check_missing_values(df, ['order_id', 'customer_id'])
            self.dq_checker.check_duplicates(df, ['order_id'])
            self.dq_checker.check_value_range(df, 'total_amount', min_val=0)
            self.dq_checker.log_issues('orders')
            self.rejected_records.extend(self.dq_checker.get_rejected_records())
            
            self.loaded_data['orders'] = df
            logger.info(f"✅ Processed {len(df)} orders")
        
        if not self.loaded_data['products'].empty:
            logger.info("Processing products...")
            df = self.loaded_data['products'].copy()
            
            if 'price' in df.columns:
                df['price'] = df['price'].apply(clean_currency)
            
            self.dq_checker.clear()
            self.dq_checker.check_missing_values(df, ['product_id', 'product_name'])
            self.dq_checker.check_duplicates(df, ['product_id'])
            self.dq_checker.log_issues('products')
            self.rejected_records.extend(self.dq_checker.get_rejected_records())
            
            self.loaded_data['products'] = df
            logger.info(f"✅ Processed {len(df)} products")
        
        if not self.loaded_data['events'].empty:
            logger.info("Processing events...")
            df = self.loaded_data['events'].copy()
            
            if 'event_date' in df.columns:
                df['event_date'] = df['event_date'].apply(clean_date)
            if 'duration_seconds' in df.columns:
                df['duration_seconds'] = pd.to_numeric(df['duration_seconds'], errors='coerce').fillna(0)
            
            self.dq_checker.clear()
            self.dq_checker.check_missing_values(df, ['event_id', 'user_id'])
            self.dq_checker.log_issues('events')
            self.rejected_records.extend(self.dq_checker.get_rejected_records())
            
            self.loaded_data['events'] = df
            logger.info(f"✅ Processed {len(df)} events")
        
        if not self.loaded_data['payments'].empty:
            logger.info("Processing payments...")
            df = self.loaded_data['payments'].copy()
            
            if 'payment_date' in df.columns:
                df['payment_date'] = df['payment_date'].apply(clean_date)
            if 'amount' in df.columns:
                df['amount'] = df['amount'].apply(clean_currency)
            
            self.dq_checker.clear()
            self.dq_checker.check_missing_values(df, ['payment_id', 'order_id'])
            self.dq_checker.check_value_range(df, 'amount', min_val=0)
            self.dq_checker.log_issues('payments')
            self.rejected_records.extend(self.dq_checker.get_rejected_records())
            
            self.loaded_data['payments'] = df
            logger.info(f"✅ Processed {len(df)} payments")
        
        if self.rejected_records:
            logger.warning(f"Total rejected records: {len(self.rejected_records)}")
            for record in self.rejected_records[:5]:  # Show first 5
                logger.warning(f"  - {record.get('issue', 'Unknown issue')}")
        
        logger.info("✅ Transformation completed successfully")
        return self.loaded_data
    
    def load(self, table_name, df, schema='public', if_exists='replace'):
        try:
            if df.empty:
                logger.warning(f"No data to load into {table_name}")
                return False
            
            df.to_sql(
                table_name,
                self.engine,
                schema=schema,
                if_exists=if_exists,
                index=False,
                chunksize=1000,
                method='multi'
            )
            logger.info(f"✅ Loaded {len(df)} records to {schema}.{table_name}")
            return True
        except Exception as e:
            logger.error(f"Error loading {table_name}: {e}")
            return False
    
    def load_all(self):
        logger.info("=" * 50)
        logger.info("Starting LOAD process...")
        logger.info("=" * 50)
        
        success_count = 0
        for table_name, df in self.loaded_data.items():
            if not df.empty:
                if self.load(f'stg_{table_name}', df, if_exists='replace'):
                    success_count += 1
        
        logger.info(f"✅ Loaded {success_count} tables successfully")
        return True
    
    def run(self):
        logger.info("=" * 60)
        logger.info("🚀 STARTING ETL PIPELINE")
        logger.info("=" * 60)
        
        try:
            self.extract()
            self.transform()
            self.load_all()
            
            logger.info("=" * 60)
            logger.info("✅ ETL PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            return True
        except Exception as e:
            logger.error(f"❌ ETL pipeline failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
