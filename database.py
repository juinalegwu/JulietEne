import sqlite3


# Connect to database
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


# Products table
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

# Payments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    reference TEXT,
    payment_date TEXT NOT NULL
)
""")

# Add amount_paid column if it doesn't exist
cursor.execute("PRAGMA table_info(orders)")
columns = [column[1] for column in cursor.fetchall()]

if "amount_paid" not in columns:
    cursor.execute("""
        ALTER TABLE orders
        ADD COLUMN amount_paid INTEGER NOT NULL DEFAULT 0
    """)


# Order items table
cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price INTEGER NOT NULL
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


# Save a new order
def save_order(customer_name, total, payment_method, payment_status, reference, order_date, orders, amount_paid=0):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO orders (
        customer_name,
        total,
        payment_method,
        payment_status,
        reference,
        order_date,
        amount_paid
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_name,
        total,
        payment_method,
        payment_status,
        reference,
        order_date,
        amount_paid
    ))

    order_id = cursor.lastrowid

    for item, price, quantity in orders:
        cursor.execute("""
        INSERT INTO order_items (
            order_id,
            product_name,
            quantity,
            unit_price
        )
        VALUES (?, ?, ?, ?)
        """, (order_id, item, quantity, price))

    connection.commit()
    connection.close()

# Get order history
def get_order_history():
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        orders.id,
        orders.customer_name,
        orders.total,
        orders.amount_paid,
        orders.payment_method,
        orders.payment_status,
        orders.reference,
        orders.order_date,
        order_items.product_name,
        order_items.quantity,
        order_items.unit_price
    FROM orders
    LEFT JOIN order_items
    ON orders.id = order_items.order_id
    ORDER BY orders.id DESC, order_items.id ASC
    """)

    orders = cursor.fetchall()

    connection.close()

    return orders


# Search for one order
def search_order(order_id):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM orders
        WHERE id = ?
    """, (order_id,))

    order = cursor.fetchone()

    connection.close()

    return order


# Get items belonging to one order
def get_order_items(order_id):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_name, quantity, unit_price
        FROM order_items
        WHERE order_id = ?
    """, (order_id,))

    items = cursor.fetchall()

    connection.close()

    return items

# Delete an order
def delete_order(order_id):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM order_items WHERE order_id = ?",
        (order_id,)
    )

    cursor.execute(
        "DELETE FROM orders WHERE id = ?",
        (order_id,)
    )

    connection.commit()
    connection.close()

# Update customer name on an order
def update_order_customer(order_id, new_name):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE orders
        SET customer_name = ?
        WHERE id = ?
    """, (new_name, order_id))

    connection.commit()
    connection.close()

def update_order_items(order_id, total, orders):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    # Get the amount already paid
    cursor.execute("""
        SELECT amount_paid
        FROM orders
        WHERE id = ?
    """, (order_id,))

    order = cursor.fetchone()

    if order is None:
        connection.close()
        return False

    amount_paid = order[0]
    if total < amount_paid:
        connection.close()
        return False

    # Calculate the correct payment status
    if amount_paid == 0:
        status = "UNPAID"

    elif amount_paid < total:
        status = "PARTIALLY PAID"

    else:
        status = "PAID"

    # Update order total and payment status
    cursor.execute("""
        UPDATE orders
        SET total = ?, payment_status = ?
        WHERE id = ?
    """, (total, status, order_id))

    # Replace old order items
    cursor.execute("""
        DELETE FROM order_items
        WHERE order_id = ?
    """, (order_id,))

    for item, price, quantity in orders:
        cursor.execute("""
            INSERT INTO order_items (
                order_id,
                product_name,
                quantity,
                unit_price
            )
            VALUES (?, ?, ?, ?)
        """, (order_id, item, quantity, price))

    connection.commit()
    connection.close()

    return True

# Record an additional payment
def record_payment(order_id, amount, payment_method, reference, payment_date):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO payments (
            order_id,
            amount,
            payment_method,
            reference,
            payment_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (order_id, amount, payment_method, reference, payment_date))

    connection.commit()
    connection.close()

# Update order payment details
def update_order_payment(order_id, amount_paid):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT total
        FROM orders
        WHERE id = ?
    """, (order_id,))

    order = cursor.fetchone()

    if order is None:
        connection.close()
        return False

    total = order[0]

    if amount_paid < 0 or amount_paid > total:
        connection.close()
        return False

    if amount_paid == 0:
        status = "UNPAID"
    elif amount_paid < total:
        status = "PARTIALLY PAID"
    else:
        status = "PAID"

    cursor.execute("""
        UPDATE orders
        SET amount_paid = ?, payment_status = ?
        WHERE id = ?
    """, (amount_paid, status, order_id))

    connection.commit()
    connection.close()

    return True


# Add an additional payment and update the order
def add_payment(order_id, amount, payment_method, reference, payment_date):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT total, amount_paid
        FROM orders
        WHERE id = ?
    """, (order_id,))

    order = cursor.fetchone()

    if order is None:
        connection.close()
        return False

    total, current_paid = order
    new_amount_paid = current_paid + amount

    if amount <= 0 or new_amount_paid > total:
        connection.close()
        return False

    if new_amount_paid == total:
        status = "PAID"
    else:
        status = "PARTIALLY PAID"

    cursor.execute("""
        INSERT INTO payments (
            order_id, amount, payment_method, reference, payment_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (order_id, amount, payment_method, reference, payment_date))

    cursor.execute("""
        UPDATE orders
        SET amount_paid = ?, payment_status = ?
        WHERE id = ?
    """, (new_amount_paid, status, order_id))

    connection.commit()
    connection.close()

    return True

# Get complete payment history for an order
def get_order_payments(order_id):
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    # Get original order payment details
    cursor.execute("""
        SELECT amount_paid, payment_method, reference, order_date
        FROM orders
        WHERE id = ?
    """, (order_id,))

    order = cursor.fetchone()

    if order is None:
        connection.close()
        return []

    total_paid, original_method, original_reference, order_date = order

    # Get additional payments
    cursor.execute("""
        SELECT amount, payment_method, reference, payment_date
        FROM payments
        WHERE order_id = ?
        ORDER BY id ASC
    """, (order_id,))

    additional_payments = cursor.fetchall()

    # Calculate the original payment
    additional_total = sum(payment[0] for payment in additional_payments)
    original_amount = total_paid - additional_total

    payments = []

    if original_amount > 0:
        payments.append((
            original_amount,
            original_method,
            original_reference,
            order_date
        ))

    payments.extend(additional_payments)

    connection.close()

    return payments