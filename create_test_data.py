import pandas as pd
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import random
import os

def create_test_data():
    os.makedirs('data', exist_ok=True)
    
    customers_data = {
        'customer_id': [f'CUST{str(i).zfill(4)}' for i in range(1, 101)],
        'first_name': [f'FirstName{i}' for i in range(1, 101)],
        'last_name': [f'LastName{i}' for i in range(1, 101)],
        'email': [f'user{i}@example.com' for i in range(1, 101)],
        'phone': [f'+1-555-{str(i).zfill(4)}' for i in range(1, 101)],
        'registration_date': [
            (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d') 
            for _ in range(100)
        ],
        'customer_segment': [random.choice(['Retail', 'Wholesale', 'Premium']) for _ in range(100)]
    }
    customers_df = pd.DataFrame(customers_data)
    customers_df.to_csv('data/customers.csv', index=False)
    print("✅ Created customers.csv")
    
    products_data = {
        'product_id': [f'PROD{str(i).zfill(3)}' for i in range(1, 51)],
        'product_name': [f'Product_{i}' for i in range(1, 51)],
        'category': [random.choice(['Electronics', 'Clothing', 'Books', 'Food', 'Furniture']) for _ in range(50)],
        'subcategory': [random.choice(['SubA', 'SubB', 'SubC']) for _ in range(50)],
        'price': [round(random.uniform(10, 500), 2) for _ in range(50)],
        'cost': [round(random.uniform(5, 300), 2) for _ in range(50)]
    }
    products_df = pd.DataFrame(products_data)
    products_df.to_excel('data/products.xlsx', index=False)
    print("✅ Created products.xlsx")
    
    orders = []
    for i in range(1, 201):
        orders.append({
            'order_id': f'ORD{str(i).zfill(4)}',
            'customer_id': f'CUST{str(random.randint(1, 100)).zfill(4)}',
            'product_id': f'PROD{str(random.randint(1, 50)).zfill(3)}',
            'quantity': random.randint(1, 10),
            'unit_price': round(random.uniform(10, 500), 2),
            'total_amount': round(random.uniform(10, 5000), 2),
            'order_date': (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d %H:%M:%S'),
            'order_status': random.choice(['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']),
            'payment_id': f'PAY{str(i).zfill(4)}'
        })
    
    with open('data/orders.json', 'w') as f:
        json.dump(orders, f, indent=2)
    print("✅ Created orders.json")
    
    root = ET.Element('events')
    for i in range(1, 501):
        event = ET.SubElement(root, 'event')
        ET.SubElement(event, 'event_id').text = f'EVT{str(i).zfill(4)}'
        ET.SubElement(event, 'user_id').text = f'CUST{str(random.randint(1, 100)).zfill(4)}'
        ET.SubElement(event, 'event_date').text = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S')
        ET.SubElement(event, 'event_type').text = random.choice(['view', 'click', 'add_to_cart', 'purchase'])
        ET.SubElement(event, 'event_category').text = random.choice(['product', 'checkout', 'homepage'])
        ET.SubElement(event, 'page_visited').text = f'/page/{random.randint(1, 20)}'
        ET.SubElement(event, 'duration_seconds').text = str(random.randint(1, 300))
        ET.SubElement(event, 'device_type').text = random.choice(['desktop', 'mobile', 'tablet'])
        ET.SubElement(event, 'browser').text = random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])
    
    tree = ET.ElementTree(root)
    tree.write('data/events.xml', encoding='utf-8', xml_declaration=True)
    print("✅ Created events.xml")
    
    payments_data = {
        'payment_id': [f'PAY{str(i).zfill(4)}' for i in range(1, 201)],
        'order_id': [f'ORD{str(i).zfill(4)}' for i in range(1, 201)],
        'payment_method': [random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer']) for _ in range(200)],
        'amount': [round(random.uniform(10, 5000), 2) for _ in range(200)],
        'payment_date': [(datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(200)],
        'status': [random.choice(['Completed', 'Pending', 'Failed']) for _ in range(200)]
    }
    payments_df = pd.DataFrame(payments_data)
    payments_df.to_csv('data/payments.csv', index=False)
    print("✅ Created payments.csv")
    
    print("\n All test data created successfully!")

if __name__ == "__main__":
    create_test_data()
