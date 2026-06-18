from loguru import logger
from src.etl_pipeline import ETLPipeline
from src.dwh_builder import DWHBuilder
from src.utils import setup_logging
import sys
import os

def main():
    setup_logging()
    
    if not os.path.exists('./data/customers.csv'):
        logger.warning("Test data not found. Creating test data...")
        try:
            from create_test_data import create_test_data
            create_test_data()
        except ImportError:
            logger.error("create_test_data module not found. Please run: python create_test_data.py")
            return 1
    
    logger.info("=" * 60)
    logger.info("🚀 STARTING ETL PROCESS")
    logger.info("=" * 60)
    
    etl = ETLPipeline()
    if not etl.run():
        logger.error("❌ ETL pipeline failed. Exiting.")
        return 1
    
    dwh = DWHBuilder()
    if not dwh.build():
        logger.error("❌ DWH build failed. Exiting.")
        return 1
    
    logger.info("=" * 60)
    logger.info("🎉 ETL PROCESS COMPLETED SUCCESSFULLY!")
    logger.info("📊 DWH is ready for analytics queries.")
    logger.info("💡 Run SQL queries from sql/analytics.sql")
    logger.info("=" * 60)
    
    from src.config import Config
    logger.info(f"📝 Database: {Config.DB_NAME} on {Config.DB_HOST}:{Config.DB_PORT}")
    logger.info(f"🔗 Connection: {Config.get_db_url()}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
