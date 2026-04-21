import sqlite3
import random
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_config import DB_PATH

def generate_mock_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        product_name TEXT,
        category TEXT,
        current_stock INTEGER
    )
    ''')

    # Create Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        contact_number TEXT,
        profile_pic TEXT
    )
    ''')
    
    # Create Sales Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        product_id TEXT,
        sales_quantity INTEGER,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')
    
    # Clear existing
    cursor.execute('DELETE FROM sales')
    cursor.execute('DELETE FROM products')
    cursor.execute('DELETE FROM users')
    
    # Add Default Mock User
    import hashlib
    pw_hash = hashlib.sha256("password123".encode()).hexdigest()
    cursor.execute('''
    INSERT INTO users (username, email, password_hash, contact_number, profile_pic)
    VALUES (?, ?, ?, ?, ?)
    ''', ("Anna C.", "anna@reckon.ai", pw_hash, "555-0199", "https://lh3.googleusercontent.com/aida-public/AB6AXuB6yVCD-0yhCRntEs7Htxrq1yG6-QPpWiWBq6gioKjNLQxbQoSeh4cfJUteJH0Ert2PgtLvF35zz7bAkCNlXAYHLTb91FEhA98Sk4YGbQ_YoifH-BrI-0K0jIYOJfwDTbecOuSbUzJS65TqCfeb9QisuVsqNdEkmvGwDXOOHCHhrT6_3l6zPAFgRxSQZVOW43J5kjapVW_ceMfa8lNptd8V8LFF72HhjFKOZGNhB-F39uLsWjc5AtcNaLvjf9YuWnDwdJ4GXWkmF3U"))

    products = [
        ('PROD-ELEC-01', 'Smart TV 55"', 'Electronics', 150),
        ('PROD-ELEC-02', 'Wireless Earbuds', 'Electronics', 300),
        ('PROD-ELEC-03', 'Laptop 14 inch', 'Electronics', 120),
        ('PROD-ELEC-04', 'Bluetooth Speaker', 'Electronics', 220),
        ('PROD-ELEC-05', 'Gaming Mouse', 'Electronics', 350),
        ('PROD-ELEC-06', 'Mechanical Keyboard', 'Electronics', 180),
        ('PROD-ELEC-07', 'Smartphone 128GB', 'Electronics', 400),
        ('PROD-ELEC-08', 'Tablet 10 inch', 'Electronics', 160),
        ('PROD-ELEC-09', 'Smartwatch Series 5', 'Electronics', 210),
        ('PROD-ELEC-10', 'Noise Cancelling Headphones', 'Electronics', 140),
        ('PROD-ELEC-11', 'Portable SSD 1TB', 'Electronics', 90),
        ('PROD-ELEC-12', '4K Action Camera', 'Electronics', 75),
        ('PROD-ELEC-13', 'WiFi Router', 'Electronics', 130),
        ('PROD-ELEC-14', 'External Hard Drive 2TB', 'Electronics', 85),
        ('PROD-ELEC-15', 'Monitor 24 inch', 'Electronics', 95),
        ('PROD-ELEC-16', 'USB-C Hub', 'Electronics', 200),
        ('PROD-ELEC-17', 'Graphics Tablet', 'Electronics', 60),
        ('PROD-ELEC-18', 'Power Bank 20000mAh', 'Electronics', 250),

        ('PROD-GROC-01', 'Organic Apples', 'Grocery', 500),
        ('PROD-GROC-02', 'Almond Milk', 'Grocery', 200),
        ('PROD-GROC-03', 'Brown Bread', 'Grocery', 300),
        ('PROD-GROC-04', 'Whole Wheat Flour', 'Grocery', 450),
        ('PROD-GROC-05', 'Basmati Rice', 'Grocery', 600),
        ('PROD-GROC-06', 'Cooking Oil 1L', 'Grocery', 350),
        ('PROD-GROC-07', 'Eggs Pack of 12', 'Grocery', 500),
        ('PROD-GROC-08', 'Bananas', 'Grocery', 700),
        ('PROD-GROC-09', 'Tomatoes', 'Grocery', 650),
        ('PROD-GROC-10', 'Potatoes', 'Grocery', 800),
        ('PROD-GROC-11', 'Green Tea Pack', 'Grocery', 200),
        ('PROD-GROC-12', 'Peanut Butter', 'Grocery', 180),
        ('PROD-GROC-13', 'Sugar 1kg', 'Grocery', 550),
        ('PROD-GROC-14', 'Salt Pack', 'Grocery', 600),
        ('PROD-GROC-15', 'Milk 1L', 'Grocery', 750),
        ('PROD-GROC-16', 'Cheese Slices', 'Grocery', 220),
        ('PROD-GROC-17', 'Butter 500g', 'Grocery', 210),

        ('PROD-FASH-01', 'Denim Jacket', 'Fashion', 100),
        ('PROD-FASH-02', 'Running Shoes', 'Fashion', 250),
        ('PROD-FASH-03', 'Cotton T-Shirt', 'Fashion', 300),
        ('PROD-FASH-04', 'Leather Wallet', 'Fashion', 120),
        ('PROD-FASH-05', 'Casual Shirt', 'Fashion', 220),
        ('PROD-FASH-06', 'Formal Trousers', 'Fashion', 150),
        ('PROD-FASH-07', 'Summer Dress', 'Fashion', 130),
        ('PROD-FASH-08', 'Sneakers', 'Fashion', 280),
        ('PROD-FASH-09', 'Hoodie Sweatshirt', 'Fashion', 190),
        ('PROD-FASH-10', 'Sports Cap', 'Fashion', 210),
        ('PROD-FASH-11', 'Sunglasses', 'Fashion', 170),
        ('PROD-FASH-12', 'Leather Belt', 'Fashion', 140),
        ('PROD-FASH-13', 'Wool Scarf', 'Fashion', 110),
        ('PROD-FASH-14', 'Track Pants', 'Fashion', 160),
        ('PROD-FASH-15', 'Blazer Jacket', 'Fashion', 90),
        ('PROD-FASH-16', 'Flip Flops', 'Fashion', 260),
        ('PROD-FASH-17', 'Handbag', 'Fashion', 180),

        ('PROD-HOME-01', 'Vacuum Cleaner', 'Home Appliances', 80),
        ('PROD-HOME-02', 'Air Purifier', 'Home Appliances', 60),
        ('PROD-HOME-03', 'Ceiling Fan', 'Home Appliances', 200),
        ('PROD-HOME-04', 'Electric Kettle', 'Home Appliances', 300),
        ('PROD-HOME-05', 'Microwave Oven', 'Home Appliances', 90),
        ('PROD-HOME-06', 'Refrigerator 300L', 'Home Appliances', 50),
        ('PROD-HOME-07', 'Washing Machine', 'Home Appliances', 70),
        ('PROD-HOME-08', 'Room Heater', 'Home Appliances', 110),
        ('PROD-HOME-09', 'Induction Cooktop', 'Home Appliances', 140),
        ('PROD-HOME-10', 'Dishwasher', 'Home Appliances', 40),
        ('PROD-HOME-11', 'Water Purifier', 'Home Appliances', 85),
        ('PROD-HOME-12', 'Air Conditioner 1.5 Ton', 'Home Appliances', 65),
        ('PROD-HOME-13', 'Toaster', 'Home Appliances', 190),
        ('PROD-HOME-14', 'Mixer Grinder', 'Home Appliances', 175),
        ('PROD-HOME-15', 'Electric Iron', 'Home Appliances', 210),
        ('PROD-HOME-16', 'Coffee Maker', 'Home Appliances', 95),
        ('PROD-HOME-17', 'Rice Cooker', 'Home Appliances', 160),
        ('PROD-HOME-18', 'Hand Blender', 'Home Appliances', 220)
    ]

    cursor.executemany('''
    INSERT INTO products (product_id, product_name, category, current_stock)
    VALUES (?, ?, ?, ?)
    ''', products)

    # 180 days of historical sales
    sales_data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    for i in range(180):
        current_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        
        for prod in products:
            prod_id = prod[0]
            category = prod[2]
            
            if category == 'Electronics':
                base_sales = random.randint(5, 20)
                if i % 14 == 0:
                    base_sales += random.randint(20, 40)
            elif category == 'Grocery':
                base_sales = random.randint(30, 80)
            else: 
                base_sales = random.randint(10, 30)
                
            sales_data.append((current_date, prod_id, base_sales))

    cursor.executemany('''
    INSERT INTO sales (date, product_id, sales_quantity)
    VALUES (?, ?, ?)
    ''', sales_data)

    conn.commit()
    conn.close()
    print(f"Successfully seeded database at {DB_PATH}")

if __name__ == '__main__':
    generate_mock_data()
