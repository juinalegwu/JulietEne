import sqlite3

connection = sqlite3.connect("bakery.db")

cursor = connection.cursor()

# Customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT
)
""")

# Remove the old products table
cursor.execute("DROP TABLE IF EXISTS products")

# Create products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price INTEGER NOT NULL
)
""")
# Orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    total INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    reference TEXT,
    order_date TEXT NOT NULL
)
""")
# Add bakery products
products = [
    ("vanilla cake", 7000),
    ("chocolate cake", 8000),
    ("red velvet cake", 9000),
    ("doughnut", 500),
    ("meat pie", 700),
    ("samosa", 500),
    ("spring roll", 500),
    ("cupcake", 600),
    ("buns", 400)
]

cursor.executemany(
    "INSERT OR IGNORE INTO products (name, price) VALUES (?, ?)",
    products
)

connection.commit()
connection.close()


# Get products from the database
def get_products():
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    connection.close()

    return products
def save_order(customer_name, total, payment_method, payment_status, reference, order_date):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO orders (
        customer_name,
        total,
        payment_method,
        payment_status,
        reference,
        order_date
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        customer_name,
        total,
        payment_method,
        payment_status,
        reference,
        order_date
    ))

    connection.commit()
    connection.close()