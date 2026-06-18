import os
from dotenv import load_dotenv
import logging

load_dotenv()

class Config:
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'etl_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    DATA_PATH = os.getenv('DATA_PATH', './data/')
    
    LOG_FILE = os.getenv('LOG_FILE', './logs/etl.log')
    
    @staticmethod
    def get_db_url():
        return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
    
    @staticmethod
    def get_db_connection_params():
        return {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'database': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD
        }
