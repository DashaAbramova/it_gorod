import pandas as pd
import xmltodict
import json
from datetime import datetime
import hashlib
from loguru import logger
import os

def read_csv(file_path):
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return pd.DataFrame()
        return pd.read_csv(file_path)
    except Exception as e:
        logger.error(f"Error reading CSV {file_path}: {e}")
        return pd.DataFrame()

def read_json(file_path):
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return pd.DataFrame()
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # If data is dict with a list inside, extract the list
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    return pd.DataFrame(value)
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Error reading JSON {file_path}: {e}")
        return pd.DataFrame()

def read_xlsx(file_path):
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return pd.DataFrame()
        return pd.read_excel(file_path)
    except Exception as e:
        logger.error(f"Error reading XLSX {file_path}: {e}")
        return pd.DataFrame()

def read_xml(file_path):
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return pd.DataFrame()
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_data = f.read()
        data = xmltodict.parse(xml_data)
        
        # Try to find the list of records in XML
        def find_records(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, list) and value and isinstance(value[0], dict):
                        return value
                    result = find_records(value)
                    if result is not None:
                        return result
            return None
        
        records = find_records(data)
        if records:
            return pd.DataFrame(records)
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error reading XML {file_path}: {e}")
        return pd.DataFrame()

def generate_hash(row, columns):
    hash_string = ''.join(str(row.get(col, '')) for col in columns)
    return hashlib.md5(hash_string.encode()).hexdigest()

def clean_date(date_str):
    if pd.isna(date_str) or date_str is None:
        return None
    try:
        if isinstance(date_str, (pd.Timestamp, datetime)):
            return date_str
        if isinstance(date_str, str):
            # Try different date formats
            formats = [
                '%Y-%m-%d', 
                '%d/%m/%Y', 
                '%m/%d/%Y', 
                '%Y-%m-%d %H:%M:%S',
                '%d-%m-%Y',
                '%Y/%m/%d'
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            # Try pandas to_datetime as fallback
            return pd.to_datetime(date_str)
        return date_str
    except Exception as e:
        logger.warning(f"Could not parse date: {date_str}, error: {e}")
        return None

def clean_currency(value):
    if pd.isna(value) or value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Remove currency symbols, commas, and spaces
        cleaned = value.replace('$', '').replace('€', '').replace('£', '') \
                       .replace(',', '').replace(' ', '').strip()
        try:
            return float(cleaned)
        except ValueError:
            logger.warning(f"Could not parse currency: {value}")
            return 0.0
    return float(value)

def validate_email(email):
    if pd.isna(email) or not isinstance(email, str):
        return False
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def setup_logging():
    import sys
    from pathlib import Path
    
    Path("./logs").mkdir(exist_ok=True)
    
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan> | <level>{message}</level>")
    logger.add("./logs/etl.log", rotation="500 MB", level="DEBUG", 
               format="{time} | {level} | {name} | {message}")
