import mysql.connector
from faker import Faker
import random
from tqdm import tqdm
import json

# ---------------------------
# Load DB credentials from config.json
# ---------------------------
with open('config.json') as f:
    config = json.load(f)

db_config = config['db']

# ---------------------------
# Database Connection
# ---------------------------
conn = mysql.connector.connect(
    host=db_config['host'],
    user=db_config['user'],
    password=db_config['password'],
    database=db_config['database']
)

cursor = conn.cursor()
fake = Faker()

# ---------------------------
# 1. Categories
# ---------------------------
categories = [
    "Cricket", "Football", "Hockey", "Tennis", "Swimming",
    "Gym", "Baseball", "Basketball", "Badminton", "Surfing"
]

for cat in categories:
    cursor.execute("INSERT INTO categories (category_name, description) VALUES (%s, %s)",
                   (cat, f"{cat} sports equipment"))
conn.commit()

cursor.execute("SELECT category_id, category_name FROM categories")
category_data = cursor.fetchall()  # [(id, name), ...]

# ---------------------------
# 2. Products
# ---------------------------
product_types = [
    "Ball", "Racket", "Shoes", "Bike", "Dumbbell",
    "Bat", "Hurling Bat", "Baseball Bat", "Helmet", "Jersey",
    "Kneepad", "Swimming Goggles", "Nets", "Gloves", "Pads",
    "Soccer Ball", "Tennis Ball", "Cricket Pads", "Cricket Gloves",
    "Hockey Stick", "Baseball Glove", "Running Shoes", "Gym Mat",
    "Water Bottle", "Backpack", "Weight Plates", "Skipping Rope",
    "Punching Bag", "Boxing Gloves", "Treadmill", "Elliptical Machine",
    "Fitness Tracker", "Yoga Mat", "Resistance Bands", "Soccer Jersey",
    "Football Helmet", "Shin Guards", "Goalkeeper Gloves", "Swim Cap",
    "Kickboard", "Pull Buoy", "Wristband", "Headband", "Sweatband",
    "Basketball", "Basketball Hoop", "Golf Club", "Golf Ball", "Hurdles",
    "Speed Ladder", "Cone Markers", "Agility Poles", "Table Tennis Paddle",
    "Table Tennis Ball", "Ice Skates", "Ski Poles", "Ski Boots",
    "Snowboard", "Surfboard", "Kayak Paddle", "Life Jacket"
]

products = []
for category_id, category_name in category_data:
    for _ in range(10):  # generate 10 products per category
        product_name = f"{fake.word().capitalize()} {random.choice(product_types)}"
        price = round(random.uniform(10, 500), 2)
        stock = random.randint(50, 1000)
        description = fake.text(max_nb_chars=100)
        products.append((product_name, category_id, price, stock, description))

cursor.executemany(
    "INSERT INTO products (product_name, category_id, price, stock_quantity, description) VALUES (%s,%s,%s,%s,%s)",
    products
)
conn.commit()

cursor.execute("SELECT product_id, price, stock_quantity FROM products")
products_data = cursor.fetchall()  # [(id, price, stock), ...]

# ---------------------------
# 3. Inventory
# ---------------------------
inventory = [(product_id, stock_quantity) for product_id, price, stock_quantity in products_data]
cursor.executemany(
    "INSERT INTO inventory (product_id, quantity) VALUES (%s, %s)",
    inventory
)
conn.commit()

# ---------------------------
# 4. Customers
# ---------------------------
batch_size = 5000
total_customers = 100_000

for batch_start in tqdm(range(0, total_customers, batch_size), desc="Generating Customers"):
    customers = []
    for _ in range(batch_size):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        phone = fake.phone_number()
        address = fake.address()
        customers.append((first_name, last_name, email, phone, address))
    cursor.executemany(
        "INSERT INTO customers (first_name, last_name, email, phone, address) VALUES (%s,%s,%s,%s,%s)",
        customers
    )
    conn.commit()

cursor.execute("SELECT customer_id FROM customers")
customer_ids = [row[0] for row in cursor.fetchall()]

# ---------------------------
# 5. Orders and Order Items (with Inventory update)
# ---------------------------
order_id_counter = 1
batch_orders = []
batch_items = []
inventory_updates = []

for customer_id in tqdm(customer_ids, desc="Generating Orders & Items"):
    num_orders = random.randint(1, 5)
    for _ in range(num_orders):
        order_date = fake.date_time_this_year()
        total_amount = 0
        order_items = []

        num_items = random.randint(1, 5)
        selected_products = random.sample(products_data, num_items)
        for product_id, price, stock_quantity in selected_products:
            quantity = random.randint(1, min(3, stock_quantity))
            total_amount += price * quantity
            order_items.append((order_id_counter, product_id, quantity, price))
            inventory_updates.append((quantity, product_id))

        batch_orders.append((customer_id, order_date, round(total_amount, 2), "Completed"))
        batch_items.extend(order_items)
        order_id_counter += 1

# Insert orders
cursor.executemany(
    "INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (%s,%s,%s,%s)",
    batch_orders
)
conn.commit()

# Insert order_items
cursor.executemany(
    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s,%s,%s,%s)",
    batch_items
)
conn.commit()

# Update inventory
cursor.executemany(
    "UPDATE inventory SET quantity = quantity - %s WHERE product_id = %s",
    inventory_updates
)
conn.commit()

print("Mock data generation completed successfully!")

cursor.close()
conn.close()
