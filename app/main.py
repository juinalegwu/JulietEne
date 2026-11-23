import sqlite3
from pathlib import Path
from fastapi import FastAPI, Request, Form
import os
import secrets
from dotenv import load_dotenv
from pwdlib import PasswordHash
from starlette.middleware.sessions import SessionMiddleware

from datetime import datetime
from database import save_order, get_order_history, add_payment, delete_order, update_order_customer, update_order_items, backup_database
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from reports import generate_full_report
from fastapi import FastAPI, Request, Form, HTTPException

load_dotenv()

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE = BASE_DIR / "bakery.db"



app = FastAPI(title="Juliet's Sweet Treats")



app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "app" / "static"),
    name="static"
)

@app.middleware("http")
async def protect_admin_pages(request: Request, call_next):

    if (
        request.url.path in ["/", "/login", "/shop", "/place-order"]
        or request.url.path.startswith("/static/")
    ):
        return await call_next(request)
    if not request.session.get("admin"):
        return RedirectResponse("/login", status_code=303)

    return await call_next(request)




app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=3600,
    same_site="lax",
    https_only=False
)

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
@app.get("/")
def public_home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"request": request}
    )
@app.get("/shop")
def shop(request: Request):
    products = get_products()

    return templates.TemplateResponse(
        request=request,
        name="shop.html",
        context={
            "request": request,
            "products": products
        }
    )
@app.get("/place-order")
def place_order(request: Request, product_id: int = None):
    products = get_products()

    return templates.TemplateResponse(
        request=request,
        name="place_order.html",
        context={
            "request": request,
            "products": products,
            "csrf_token": get_csrf_token(request),
            "selected_product_id": product_id
        }
    )
def get_csrf_token(request: Request):
    token = request.session.get("csrf_token")

    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token

    return token

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "csrf_token": get_csrf_token(request)
        }
    )
@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...)
):
    if not secrets.compare_digest(
        csrf_token,
        request.session.get("csrf_token", "")
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "csrf_token": get_csrf_token(request),
                "error": "Invalid security token. Please try again."
            },
            status_code=403
        )

    if (
        username != ADMIN_USERNAME
        or not password_hash.verify(password, ADMIN_PASSWORD_HASH)
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "csrf_token": get_csrf_token(request),
                "error": "Invalid username or password."
            },
            status_code=401
        )

    request.session["admin"] = True

    return RedirectResponse("/admin", status_code=303)
@app.post("/logout")
def logout(
    request: Request,
    csrf_token: str = Form(...)
):
    if not secrets.compare_digest(
        csrf_token,
        request.session.get("csrf_token", "")
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid security token."
        )

    request.session.clear()

    return RedirectResponse("/login", status_code=303)
@app.on_event("startup")
def create_startup_backup():
    backup_database()


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


@app.get("/admin")
def home(request: Request):

    stats = get_dashboard_stats()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            **stats,
            "csrf_token": get_csrf_token(request)
        }
    )

@app.get("/export-report")
def export_report():

    report_path = generate_full_report()

    return FileResponse(
        path=report_path,
        filename=report_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.get("/new-order")
def new_order(request: Request):

    products = get_products()

    return templates.TemplateResponse(
        request=request,
        name="new_order.html",
        context={
            "products": products,
            "csrf_token": get_csrf_token(request)
        }
    )

@app.post("/new-order")
async def create_order(
    request: Request,
    customer_name: str = Form(...),
    customer_phone: str = Form(""),
    csrf_token: str = Form(...)
    
):

    if not secrets.compare_digest(
        csrf_token,
        request.session.get("csrf_token", "")
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid security token."
        )
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
        url="/admin",
        status_code=303
    )

@app.post("/place-order")
async def submit_customer_order(
    request: Request,
    customer_name: str = Form(...),
    customer_phone: str = Form(...),
    csrf_token: str = Form(...)
):
    if not secrets.compare_digest(
        csrf_token,
        request.session.get("csrf_token", "")
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid security token."
        )

    form = await request.form()
    products = get_products()

    orders = []
    total = 0

    for product in products:
        product_id = product[0]
        product_name = product[1]
        price = product[2]

        try:
            quantity = int(form.get(f"quantity_{product_id}", 0) or 0)
        except (ValueError, TypeError):
            return RedirectResponse("/place-order", status_code=303)

        if quantity < 0:
            return RedirectResponse("/place-order", status_code=303)

        if quantity > 0:
            orders.append((product_name, price, quantity))
            total += price * quantity

    if not customer_name.strip() or not customer_phone.strip() or not orders:
        return RedirectResponse("/place-order", status_code=303)

    customer_name = customer_name.strip()
    customer_phone = customer_phone.strip()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    existing_customer = cursor.execute(
        "SELECT id FROM customers WHERE name = ?",
        (customer_name,)
    ).fetchone()

    if existing_customer:
        cursor.execute(
            "UPDATE customers SET phone = ? WHERE id = ?",
            (customer_phone, existing_customer[0])
        )
    else:
        cursor.execute(
            "INSERT INTO customers (name, phone) VALUES (?, ?)",
            (customer_name, customer_phone)
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

    return RedirectResponse("/shop?order=received", status_code=303)

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
def order_details(request: Request, order_id: int, error: str = None):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    order = cursor.execute(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()

    if not order:
        connection.close()
        return {"error": "Order not found"}

    customer_phone = cursor.execute(
        "SELECT phone FROM customers WHERE name = ?",
        (order[1],)
    ).fetchone()

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
        "payments": payments,
        "csrf_token": get_csrf_token(request),
        "customer_phone": customer_phone[0] if customer_phone else "Not provided",
        "else": error    
    }
)

@app.post("/orders/{order_id}/payment")
def record_order_payment(
    request: Request,
    order_id: int,
    amount: int = Form(...),
    payment_method: str = Form(...),
    reference: str = Form(""),
    csrf_token: str = Form(...)
):
    if not secrets.compare_digest(
        csrf_token,
        request.session.get("csrf_token", "")
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid security token."
        )
    payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    success = add_payment(
        order_id,
        amount,
        payment_method,
        reference or None,
        payment_date,
        db_path=str(DATABASE)
    )

    if not success:
        return RedirectResponse(
            url=f"/orders/{order_id}?error=payment",
            status_code=303
        )

    return RedirectResponse(
        url=f"/orders/{order_id}",
        status_code=303
    )

@app.post("/orders/{order_id}/delete")
def delete_order_page(request: Request, order_id: int, csrf_token: str = Form(...)):
    delete_order(order_id)

    return RedirectResponse(
        url="/orders",
        status_code=303
    )
    if not secrets.compare_digest(
        csrf_token,
        request.session.get("csrf_token", "")
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid security token."
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
            "error": error,
            "csrf_token": get_csrf_token(request)
        }
    )

@app.post("/orders/{order_id}/edit")
async def update_order_page(
    request: Request,
    order_id: int
):

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token", "")

    if not secrets.compare_digest(
        csrf_token,
        request.session.get("csrf_token", "")
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid security token."
        )
    form_data = await request.form()

    customer_name = form_data.get("customer_name")
    customer_phone = form_data.get("customer_phone", "")
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

@app.get("/download-backup/{backup_name}")
async def download_backup(backup_name: str):

    backup_folder = BASE_DIR / "backups"
    backup_path = backup_folder / backup_name

    if (
        not backup_path.is_file()
        or backup_path.parent != backup_folder
        or not backup_name.startswith("bakery_backup_")
        or not backup_name.endswith(".db")
    ):
        raise HTTPException(
            status_code=404,
            detail="Backup file not found."
        )

    return FileResponse(
        path=backup_path,
        filename=backup_name,
        media_type="application/octet-stream"
    )

@app.get("/backups")
async def view_backups(request: Request):

    backup_folder = BASE_DIR / "backups"
    backup_folder.mkdir(exist_ok=True)

    backup_files = sorted(
        backup_folder.glob("bakery_backup_*.db"),
        key=lambda file: file.stat().st_mtime,
        reverse=True
    )

    backups = [
        {
            "name": file.name,
            "date": datetime.fromtimestamp(
                file.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M:%S")
        }
        for file in backup_files
    ]

    return templates.TemplateResponse(
        request=request,
        name="backups.html",
        context={
    "backups": backups,
    "csrf_token": get_csrf_token(request),
    "message": request.query_params.get("message")
}
    )
@app.post("/restore")
async def restore_backup(
    request: Request,
    backup_name: str = Form(...),
    csrf_token: str = Form(...)
):
    if not secrets.compare_digest(
        csrf_token,
        request.session.get("csrf_token", "")
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid security token."
        )
        return {"error": "Invalid backup file"}

    source = sqlite3.connect(str(backup_path))

    try:
        result = source.execute("PRAGMA integrity_check").fetchone()

        if not result or result[0] != "ok":
            return {"error": "This backup is damaged"}

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safety_file = backup_folder / f"before_restore_{timestamp}.db"

        current = sqlite3.connect(str(DATABASE))
        safety = sqlite3.connect(str(safety_file))

        try:
            current.backup(safety)
        finally:
            safety.close()
            current.close()

        destination = sqlite3.connect(str(DATABASE))

        try:
            source.backup(destination)
        finally:
            destination.close()

    finally:
        source.close()

    return RedirectResponse(
    url="/backups?message=Database+restored+successfully",
    status_code=303
)
