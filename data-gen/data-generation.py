import mysql.connector
from faker import Faker
import random
from tqdm import tqdm
import json


class DBConnection:
    def __init__(self, config_path="../config/config.json"):
        with open(config_path) as f:
            config = json.load(f)
        db_config = config['db']
        self.conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        self.cursor = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()


class DataGenerator:
    def __init__(self, db_conn, total_customers=100000, batch_size=5000):
        self.db = db_conn
        self.fake = Faker()
        self.total_customers = total_customers
        self.batch_size = batch_size
        self.categories = [
            "Cricket", "Football", "Hockey", "Tennis", "Swimming",
            "Gym", "Baseball", "Basketball", "Badminton", "Surfing"
        ]
        self.product_types = [
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

    def create_categories(self):
        for cat in self.categories:
            self.db.cursor.execute(
                "INSERT INTO categories (category_name, description) VALUES (%s, %s)",
                (cat, f"{cat} sports equipment")
            )
        self.db.commit()
        self.db.cursor.execute("SELECT category_id, category_name FROM categories")
        self.category_data = self.db.cursor.fetchall()
        print("Categories created.")

    def create_products_and_inventory(self):
        products = []
        for category_id, _ in self.category_data:
            for _ in range(10):  # 10 products per category
                product_name = f"{self.fake.word().capitalize()} {random.choice(self.product_types)}"
                price = round(random.uniform(10, 500), 2)
                stock = random.randint(50, 1000)
                description = self.fake.text(max_nb_chars=100)
                products.append((product_name, category_id, price, stock, description))

        self.db.cursor.executemany(
            "INSERT INTO products (product_name, category_id, price, stock_quantity, description) VALUES (%s,%s,%s,%s,%s)",
            products
        )
        self.db.commit()

        self.db.cursor.execute("SELECT product_id, price, stock_quantity FROM products")
        self.products_data = self.db.cursor.fetchall()

        inventory = [(pid, stock) for pid, price, stock in self.products_data]
        self.db.cursor.executemany(
            "INSERT INTO inventory (product_id, quantity) VALUES (%s, %s)",
            inventory
        )
        self.db.commit()
        print("Products and inventory created.")

    def create_customers(self):
        for batch_start in tqdm(range(0, self.total_customers, self.batch_size), desc="Generating Customers"):
            customers = []
            for _ in range(self.batch_size):
                first_name = self.fake.first_name()
                last_name = self.fake.last_name()
                email = self.fake.unique.email()
                phone = self.fake.phone_number()
                address = self.fake.address()
                customers.append((first_name, last_name, email, phone, address))
            self.db.cursor.executemany(
                "INSERT INTO customers (first_name, last_name, email, phone, address) VALUES (%s,%s,%s,%s,%s)",
                customers
            )
            self.db.commit()

        self.db.cursor.execute("SELECT customer_id FROM customers")
        self.customer_ids = [row[0] for row in self.db.cursor.fetchall()]
        print("Customers created.")

    def create_orders_and_items(self):
        for customer_id in tqdm(self.customer_ids, desc="Generating Orders & Items"):
            num_orders = random.randint(1, 5)
            for _ in range(num_orders):
                order_date = self.fake.date_time_this_year()
                total_amount = 0
                order_items = []

                num_items = random.randint(1, 5)
                selected_products = random.sample(self.products_data, num_items)
                for product_id, price, stock_quantity in selected_products:
                    quantity = random.randint(1, min(3, stock_quantity))
                    total_amount += price * quantity
                    order_items.append((product_id, quantity, price))

                # Insert order
                self.db.cursor.execute(
                    "INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (%s,%s,%s,%s)",
                    (customer_id, order_date, round(total_amount, 2), "Completed")
                )
                order_id = self.db.cursor.lastrowid

                # Insert order_items
                items_to_insert = [(order_id, pid, qty, price) for pid, qty, price in order_items]
                self.db.cursor.executemany(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s,%s,%s,%s)",
                    items_to_insert
                )

                # Update inventory
                inventory_updates = [(qty, pid) for pid, qty, price in order_items]
                self.db.cursor.executemany(
                    "UPDATE inventory SET quantity = quantity - %s WHERE product_id = %s",
                    inventory_updates
                )
            self.db.commit()

        print("Orders and order_items created.")


if __name__ == "__main__":
    db_conn = DBConnection()
    generator = DataGenerator(db_conn)
    generator.create_categories()
    generator.create_products_and_inventory()
    generator.create_customers()
    generator.create_orders_and_items()
    db_conn.close()
    print("Data generation completed successfully!")
