import sqlite3
from pathlib import Path


from datetime import datetime
from database import save_order, get_order_history, add_payment, delete_order, update_order_customer, update_order_items
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="Juliet's Sweet Treats")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE = BASE_DIR / "bakery.db"


def get_products():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    products = cursor.execute(
        "SELECT id, name, price FROM products"
    ).fetchall()

    connection.close()

    return products


def get_dashboard_stats():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    total_orders = cursor.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    total_products = cursor.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    total_customers = cursor.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    total_sales = cursor.execute(
        "SELECT COALESCE(SUM(total), 0) FROM orders"
    ).fetchone()[0]

    amount_paid = cursor.execute(
        "SELECT COALESCE(SUM(amount_paid), 0) FROM orders"
    ).fetchone()[0]

    outstanding = total_sales - amount_paid

    connection.close()

    return {
        "total_orders": total_orders,
        "total_products": total_products,
        "total_customers": total_customers,
        "total_sales": total_sales,
        "amount_paid": amount_paid,
        "outstanding": outstanding
    }


@app.get("/")
def home(request: Request):

    stats = get_dashboard_stats()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=stats
    )


@app.get("/new-order")
def new_order(request: Request):

    products = get_products()

    return templates.TemplateResponse(
        request=request,
        name="new_order.html",
        context={"products": products}
    )

@app.post("/new-order")
async def create_order(
    request: Request,
    customer_name: str = Form(...),
    customer_phone: str = Form("")
):

    form = await request.form()

    products = get_products()

    orders = []
    total = 0

    for product in products:

        product_id = product[0]
        product_name = product[1]
        price = product[2]

        quantity = int(form.get(f"quantity_{product_id}", 0) or 0)

        if quantity > 0:
            orders.append((product_name, price, quantity))
            total += price * quantity

    if not customer_name.strip() or not orders:
        return RedirectResponse(
            url="/new-order",
            status_code=303
        )

    customer_name = customer_name.strip()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    existing_customer = cursor.execute(
        "SELECT id FROM customers WHERE name = ?",
        (customer_name,)
    ).fetchone()
    if not existing_customer:
        cursor.execute(
        "INSERT INTO customers (name, phone) VALUES (?, ?)",
        (customer_name, customer_phone)
    )
    else:
        cursor.execute(
        "UPDATE customers SET phone = ? WHERE id = ?",
        (customer_phone, existing_customer[0])
    )

    connection.commit()
    connection.close()

    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_order(
        customer_name,
        total,
        "Not Paid",
        "UNPAID",
        None,
        order_date,
        orders,
        0
    )

    return RedirectResponse(
        url="/",
        status_code=303
    )

@app.get("/search-orders")
def search_orders(request: Request, query: str = ""):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    orders = []

    if query.strip():
        if query.isdigit():
            condition = "orders.id = ?"
            value = int(query)
        else:
            condition = "orders.customer_name LIKE ?"
            value = f"%{query.strip()}%"

        cursor.execute(f"""
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
            WHERE {condition}
            ORDER BY orders.id DESC
        """, (value,))

        orders = cursor.fetchall()

    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="order_history.html",
        context={
            "orders": orders,
            "search_query": query
        }
    )

@app.get("/orders")
def order_history(request: Request):

    orders = get_order_history()

    return templates.TemplateResponse(
        request=request,
        name="order_history.html",
        context={"orders": orders}
    )

@app.get("/orders/{order_id}")
def order_details(request: Request, order_id: int):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    order = cursor.execute(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()

    if not order:
        connection.close()
        return {"error": "Order not found"}

    items = cursor.execute(
        "SELECT product_name, quantity, unit_price FROM order_items WHERE order_id = ?",
        (order_id,)
    ).fetchall()

    payments = cursor.execute(
        "SELECT amount, payment_method, reference, payment_date FROM payments WHERE order_id = ?",
        (order_id,)
    ).fetchall()

    connection.close()

    return templates.TemplateResponse(
    request=request,
    name="order_details.html",
    context={
        "order": order,
        "items": items,
        "payments": payments
    }
)

@app.post("/orders/{order_id}/payment")
def record_order_payment(
    order_id: int,
    amount: int = Form(...),
    payment_method: str = Form(...),
    reference: str = Form("")
):
    payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    success = add_payment(
        order_id,
        amount,
        payment_method,
        reference or None,
        payment_date,
        db_path=str(DATABASE)
    )

    return RedirectResponse(
        url=f"/orders/{order_id}",
        status_code=303
    )

@app.post("/orders/{order_id}/delete")
def delete_order_page(order_id: int):
    delete_order(order_id)

    return RedirectResponse(
        url="/orders",
        status_code=303
    )


@app.get("/orders/{order_id}/edit")
def edit_order_page(request: Request, order_id: int, error: str = None):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,)
    )

    order = cursor.fetchone()

    if order is None:
        connection.close()
        return {"error": "Order not found"}

    cursor.execute("""
        SELECT product_name, quantity
        FROM order_items
        WHERE order_id = ?
    """, (order_id,))

    order_items = cursor.fetchall()

    connection.close()

    products = get_products()

    return templates.TemplateResponse(
        request=request,
        name="edit_order.html",
        context={
            "order": order,
            "products": products,
            "order_items": order_items,
            "error": error
        }
    )

@app.post("/orders/{order_id}/edit")
async def update_order_page(
    request: Request,
    order_id: int
):
    form_data = await request.form()

    customer_name: str = Form(...),
    customer_phone: str = Form("")
    products = get_products()

    updated_orders = []
    new_total = 0

    for product in products:
        quantity = int(
            form_data.get(f"quantity_{product[0]}", 0)
        )

        if quantity > 0:
            updated_orders.append(
                (product[1], product[2], quantity)
            )

            new_total += product[2] * quantity

    if not updated_orders:
        return {"error": "Please select at least one product."}

    success = update_order_items(
        order_id,
        new_total,
        updated_orders
    )

    if not success:
        return RedirectResponse(
            url=f"/orders/{order_id}/edit?error=payment",
            status_code=303
    )

    update_order_customer(order_id, customer_name)

    return RedirectResponse(
        url=f"/orders/{order_id}",
        status_code=303
    )
@app.get("/customers")
def customers_page(request: Request):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    customers = cursor.execute("""
        SELECT id, name, phone
        FROM customers
        ORDER BY name
    """).fetchall()

    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="customers.html",
        context={"customers": customers}
    )
@app.get("/customers/{customer_id}")
def customer_details(request: Request, customer_id: int):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    customer = cursor.execute("""
        SELECT id, name, phone
        FROM customers
        WHERE id = ?
    """, (customer_id,)).fetchone()

    if customer is None:
        connection.close()
        return {"error": "Customer not found"}

    orders = cursor.execute("""
        SELECT id, total, amount_paid, payment_status, order_date
        FROM orders
        WHERE customer_name = ?
        ORDER BY id DESC
    """, (customer[1],)).fetchall()

    connection.close()

    total_spent = sum(order[2] for order in orders)
    outstanding = sum(order[1] - order[2] for order in orders)

    return templates.TemplateResponse(
        request=request,
        name="customer_details.html",
        context={
            "customer": customer,
            "orders": orders,
            "total_orders": len(orders),
            "total_spent": total_spent,
            "outstanding": outstanding
        }
    )
