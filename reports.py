import sqlite3
from openpyxl import Workbook
from datetime import datetime
from pathlib import Path
from openpyxl.styles import Font, PatternFill

def create_report():

    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Orders"

    sheet.append([
    "Order ID",
    "Customer Name",
    "Total",
    "Amount Paid",
    "Balance",
    "Payment Status",
    "Payment Method",
    "Order Date"
])

    return workbook

def get_orders():

    connection = sqlite3.connect("bakery.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM orders")

    orders = cursor.fetchall()

    connection.close()

    return orders


def add_orders_to_sheet(sheet):

    orders = get_orders()
    connection = sqlite3.connect("bakery.db")
    cursor = connection.cursor()

    for order in orders:

        order_id = order[0]
        customer = order[1]
        total = order[2]
        cursor.execute(
            "SELECT DISTINCT payment_method FROM payments WHERE order_id = ?",
            (order_id,)
        )

        payment_methods = [row[0] for row in cursor.fetchall()]

        payment_method = ", ".join(payment_methods) if payment_methods else "Not Paid"
        payment_status = order[4]
        order_date = order[6]
        amount_paid = order[7]

        balance = total - amount_paid

        sheet.append([
            order_id,
            customer,
            total,
            amount_paid,
            balance,
            payment_status,
            payment_method,
            order_date
        ])
        
    connection.close()


def save_report(workbook):

    report_folder = Path("reports")
    report_folder.mkdir(exist_ok=True)

    filename = datetime.now().strftime("orders_%Y-%m-%d_%H-%M-%S.xlsx")

    file_path = report_folder / filename

    from openpyxl.styles import Font, PatternFill, Alignment

    for sheet in workbook.worksheets:

        # Add report title
        sheet.insert_rows(1)
        sheet.merge_cells(
            start_row=1,
            start_column=1,
            end_row=1,
            end_column=sheet.max_column
        )

        title = sheet.cell(row=1, column=1)
        title.value = "JULIET'S SWEET TREATS - BUSINESS REPORT"
        title.font = Font(bold=True, size=16, color="FFFFFF")
        title.fill = PatternFill(
            start_color="7030A0",
            end_color="7030A0",
            fill_type="solid"
        )
        title.alignment = Alignment(horizontal="center")

        # Format column headings (now row 2)
        for cell in sheet[2]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                start_color="4472C4",
                end_color="4472C4",
                fill_type="solid"
            )

        # Adjust column widths and currency
        for column in sheet.columns:
            header = column[1].value
            column_letter = column[1].column_letter
            max_length = 0

            if header in ["Total", "Amount Paid", "Balance", "Amount", "Price", "Unit Price"]:
                for cell in column[2:]:
                    if isinstance(cell.value, (int, float)):
                        cell.number_format = '"₦"#,##0'

            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            sheet.column_dimensions[column_letter].width = max(max_length + 3, 20)

    workbook.save(file_path)

    print(f"Report saved successfully: {file_path}")
    return file_path
 

def get_payments():

    connection = sqlite3.connect("bakery.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM payments")

    payments = cursor.fetchall()

    connection.close()

    return payments

 
def add_payments_sheet(workbook):

    sheet = workbook.create_sheet("Payments")

    sheet.append([
        "Payment ID",
        "Order ID",
        "Amount",
        "Payment Method",
        "Reference",
        "Payment Date"
    ])

    return sheet
 

def add_payments_to_sheet(sheet):

    payments = get_payments()

    for payment in payments:

        sheet.append(payment)

def add_customers_sheet(workbook):

    sheet = workbook.create_sheet("Customers")

    sheet.append([
        "Customer ID",
        "Customer Name",
        "Phone Number"
    ])

    return sheet

def get_customers():

    connection = sqlite3.connect("bakery.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM customers")

    customers = cursor.fetchall()

    connection.close()

    return customers

def add_customers_to_sheet(sheet):

    customers = get_customers()

    for customer in customers:

        sheet.append(customer)

def add_products_sheet(workbook):

    sheet = workbook.create_sheet("Products")

    sheet.append([
        "Product ID",
        "Product Name",
        "Price"
    ])

    return sheet

def get_products():

    connection = sqlite3.connect("bakery.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    connection.close()

    return products

def add_products_to_sheet(sheet):

    products = get_products()

    for product in products:

        sheet.append(product)

def add_order_items_sheet(workbook):

    sheet = workbook.create_sheet("Order Items")

    sheet.append([
        "Item ID",
        "Order ID",
        "Product Name",
        "Quantity",
        "Unit Price"
    ])

    return sheet

def get_order_items():

    connection = sqlite3.connect("bakery.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM order_items")

    items = cursor.fetchall()

    connection.close()

    return items

def add_order_items_to_sheet(sheet):

    items = get_order_items()

    for item in items:

        sheet.append(item)

def generate_full_report():

    workbook = create_report()

    # Orders
    add_orders_to_sheet(workbook["Orders"])

    # Payments
    # Payments
    payments_sheet = add_payments_sheet(workbook)
    add_payments_to_sheet(payments_sheet)
    # Customers
    customers_sheet = add_customers_sheet(workbook)
    add_customers_to_sheet(customers_sheet)

    # Products
    products_sheet = add_products_sheet(workbook)
    add_products_to_sheet(products_sheet)

    # Order Items
    items_sheet = add_order_items_sheet(workbook)
    add_order_items_to_sheet(items_sheet)

    return save_report(workbook)