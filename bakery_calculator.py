import random
import time
from datetime import datetime

from database import (
    get_products,
    save_order,
    get_order_history,
    search_order,
    get_order_items,
    delete_order,
    update_order_customer,
    update_order_items,
    add_payment,
    get_order_payments
)


def print_header():
    print("\n" + "=" * 50)
    print("        JULIET'S SWEET TREATS")
    print("          BAKERY ORDER SYSTEM")
    print("=" * 50)


def display_menu():
    products = get_products()

    print("\n--- MENU ---")

    for product_id, name, price in products:
        print(f"{product_id}. {name.title():<20} ₦{price:,}")


def choose_item():
    products = get_products()

    while True:
        display_menu()

        try:
            choice = int(input("\nChoose an item: "))

            for product_id, name, price in products:
                if choice == product_id:
                    return name, price

            print("Invalid choice. Please choose a number from the menu.")

        except ValueError:
            print("Please enter a valid number.")


def choose_quantity():
    while True:
        try:
            quantity = int(input("Enter quantity: "))

            if quantity > 0:
                return quantity

            print("Quantity must be greater than 0.")

        except ValueError:
            print("Please enter a whole number.")


def build_order():
    orders = []

    another = "yes"

    while another.lower() == "yes":
        item, price = choose_item()
        quantity = choose_quantity()

        orders.append((item, price, quantity))

        another = input("Add another item? (yes/no): ")

    return orders


def calculate_total(orders):
    total = 0

    for item, price, quantity in orders:
        total += price * quantity

    return total


def print_cart(orders):
    print("\n--- YOUR ORDER ---")

    for item, price, quantity in orders:
        item_total = price * quantity
        print(f"{item.title()} x {quantity} = ₦{item_total:,}")

    total = calculate_total(orders)

    print("-" * 40)
    print(f"TOTAL: ₦{total:,}")


# Determine payment status
def get_payment_status(total, amount_paid):

    if amount_paid <= 0:
        return "UNPAID"

    elif amount_paid < total:
        return "PARTIALLY PAID"

    else:
        return "PAID"


# Ask how much the customer is paying
def ask_payment_amount(total):

    while True:
        try:
            amount = int(input("\nEnter amount paid (₦): "))

            if amount < 0:
                print("Amount cannot be negative.")

            elif amount > total:
                print("Amount cannot be greater than the order total.")

            else:
                return amount

        except ValueError:
            print("Please enter a valid amount.")


# Cash payment
def pay_with_cash(total):
    print("\n--- CASH PAYMENT ---")

    while True:
        try:
            amount = int(input("Enter amount received (₦): "))

            if amount < 0:
                print("Amount cannot be negative.")
                continue

            amount_paid = min(amount, total)
            change = max(amount - total, 0)

            payment_status = get_payment_status(
                total,
                amount_paid
            )

            print(f"\nAmount received: ₦{amount:,}")
            print(f"Amount paid: ₦{amount_paid:,}")
            print(f"Outstanding: ₦{total - amount_paid:,}")

            return (
                "Cash",
                payment_status,
                None,
                change,
                amount_paid
            )

        except ValueError:
            print("Please enter a valid amount.")


# Bank transfer
def pay_with_transfer(total):
    print("\n--- BANK TRANSFER ---")
    print("This is a simulated transfer for demonstration only.")

    print(f"Order total: ₦{total:,}")

    amount_paid = ask_payment_amount(total)

    payment_status = get_payment_status(
        total,
        amount_paid
    )

    if amount_paid == 0:
        print("\nNo payment received.")

        return (
            "Bank Transfer",
            payment_status,
            None,
            0,
            amount_paid
        )

    print("\n1. GTBank       *737#")
    print("2. Access Bank  *901#")
    print("3. Zenith Bank  *966#")
    print("4. First Bank   *894#")
    print("5. UBA          *919#")

    while True:
        try:
            bank = int(input("\nChoose your bank: "))

            if 1 <= bank <= 5:
                break

            print("Choose a number from 1 to 5.")

        except ValueError:
            print("Please enter a valid number.")

    print("\nProcessing transfer...")
    time.sleep(2)

    reference = f"TRF{random.randint(100000, 999999)}"

    print("Simulated transfer successful!")

    return (
        "Bank Transfer",
        payment_status,
        reference,
        0,
        amount_paid
    )


# Card payment
def pay_with_card(total):
    print("\n--- CARD PAYMENT ---")
    print("This is a simulated card payment.")

    print(f"Order total: ₦{total:,}")

    amount_paid = ask_payment_amount(total)

    payment_status = get_payment_status(
        total,
        amount_paid
    )

    if amount_paid == 0:
        print("\nNo payment received.")

        return (
            "Card",
            payment_status,
            None,
            0,
            amount_paid
        )

    print("\nEnter test card details only.")
    print("Do not use your real card number or PIN.")

    input("Enter test card number: ")
    input("Enter test PIN: ")

    print("\nProcessing card payment...")
    time.sleep(2)

    reference = f"CARD{random.randint(100000, 999999)}"

    print("Simulated card payment successful!")

    return (
        "Card",
        payment_status,
        reference,
        0,
        amount_paid
    )


# Choose payment method
def choose_payment_method(total):
    print("\n--- PAYMENT METHOD ---")
    print("1. Cash")
    print("2. Bank Transfer")
    print("3. Card")

    while True:
        try:
            choice = int(input("\nChoose payment method: "))

            if choice == 1:
                return pay_with_cash(total)

            elif choice == 2:
                return pay_with_transfer(total)

            elif choice == 3:
                return pay_with_card(total)

            else:
                print("Please choose 1, 2, or 3.")

        except ValueError:
            print("Please enter a valid number.")


# Print receipt
def print_receipt(
    customer_name,
    orders,
    total,
    payment_method,
    payment_status,
    reference,
    change,
    amount_paid
):
    print("\n" + "=" * 50)
    print("             RECEIPT")
    print("        JULIET'S SWEET TREATS")
    print("=" * 50)

    print(f"Customer: {customer_name}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("-" * 50)

    for item, price, quantity in orders:
        item_total = price * quantity

        print(
            f"{item.title()} x {quantity} "
            f"@ ₦{price:,} = ₦{item_total:,}"
        )

    outstanding = max(total - amount_paid, 0)

    print("-" * 50)
    print(f"TOTAL: ₦{total:,}")
    print(f"Amount Paid: ₦{amount_paid:,}")
    print(f"Outstanding: ₦{outstanding:,}")
    print(f"Payment: {payment_method}")
    print(f"Status: {payment_status}")

    if reference:
        print(f"Reference: {reference}")

    if change:
        print(f"Change: ₦{change:,}")

    print("=" * 50)
    print("Thank you for ordering from")
    print("Juliet's Sweet Treats!")
    print("=" * 50)


# Create a new order
def create_order():
    print_header()

    customer_name = input("\nEnter customer name: ")

    orders = build_order()

    if not orders:
        print("No items were ordered.")
        return

    print_cart(orders)

    total = calculate_total(orders)

    (
        payment_method,
        payment_status,
        reference,
        change,
        amount_paid
    ) = choose_payment_method(total)

    print_receipt(
        customer_name,
        orders,
        total,
        payment_method,
        payment_status,
        reference,
        change,
        amount_paid
    )

    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    save_order(
        customer_name,
        total,
        payment_method,
        payment_status,
        reference,
        order_date,
        orders,
        amount_paid
    )

    print("\nOrder saved successfully!")


# Search for an order
def find_order():
    print("\n--- SEARCH ORDER ---")

    try:
        order_id = int(input("Enter Order ID: "))

        order = search_order(order_id)

        if order:
            print("\n--- ORDER DETAILS ---")

            (
                order_id,
                customer_name,
                total,
                payment_method,
                payment_status,
                reference,
                order_date,
                amount_paid
            ) = order

            outstanding = max(total - amount_paid, 0)

            print(f"Order ID: {order_id}")
            print(f"Customer: {customer_name.title()}")
            print(f"Total: ₦{total:,}")
            print(f"Amount Paid: ₦{amount_paid:,}")
            print(f"Outstanding: ₦{outstanding:,}")
            print(f"Payment: {payment_method}")
            print(f"Status: {payment_status}")
            print(f"Reference: {reference}")
            print(f"Date: {order_date}")

            items = get_order_items(order_id)

            print("\n--- ITEMS PURCHASED ---")

            for product_name, quantity, unit_price in items:
                item_total = quantity * unit_price

                print(
                    f"{product_name.title()} x {quantity} "
                    f"= ₦{item_total:,}"
                )

        else:
            print("Order not found.")

    except ValueError:
        print("Please enter a valid Order ID.")


# Delete an order
def remove_order():
    print("\n--- DELETE ORDER ---")

    try:
        order_id = int(input("Enter Order ID to delete: "))

        order = search_order(order_id)

        if order:
            confirm = input(
                "Are you sure you want to delete this order? (yes/no): "
            )

            if confirm.lower() == "yes":
                delete_order(order_id)
                print("Order deleted successfully!")

            else:
                print("Order deletion cancelled.")

        else:
            print("Order not found.")

    except ValueError:
        print("Please enter a valid Order ID.")


# Edit an order
def edit_order():
    print("\n--- EDIT ORDER ---")

    try:
        order_id = int(input("Enter Order ID: "))

        order = search_order(order_id)

        if order:
            print(f"\nCurrent customer: {order[1]}")
            print(f"Current total: ₦{order[2]:,}")

            print("\n1. Edit customer name")
            print("2. Edit products and quantities")

            choice = input("Choose what to edit: ")

            if choice == "1":
                new_name = input("Enter new customer name: ")

                if new_name.strip():
                    update_order_customer(order_id, new_name)

                    print("Customer name updated successfully!")

                else:
                    print("Customer name cannot be empty.")

            elif choice == "2":
                orders = build_order()

                if orders:
                    total = calculate_total(orders)

                updated = update_order_items(order_id, total, orders)
                if updated:
                    updated_order = search_order(order_id)

                    print("\nOrder updated successfully!")
                    print(f"New total: ₦{total:,}")
                    print(f"Amount paid: ₦{updated_order[7]:,}")
                    print(f"Payment status: {updated_order[4]}")
                else:
                    print("\nOrder cannot be updated.")
                    print("The new total cannot be less than the amount already paid.")

            else:
                print("Invalid choice.")

        else:
            print("Order not found.")

    except ValueError:
        print("Please enter a valid Order ID.")

def record_additional_payment():
    print("\n--- RECORD ADDITIONAL PAYMENT ---")

    try:
        order_id = int(input("Enter Order ID: "))

        order = search_order(order_id)

        if not order:
            print("Order not found.")
            return

        total = order[2]
        amount_paid = order[7]

        outstanding = total - amount_paid

        print(f"\nOrder Total: ₦{total:,}")
        print(f"Amount Paid: ₦{amount_paid:,}")
        print(f"Outstanding: ₦{outstanding:,}")

        if outstanding <= 0:
            print("\nThis order is already fully paid.")
            return

        amount = int(input("\nEnter payment amount: ₦"))

        if amount <= 0 or amount > outstanding:
            print("Invalid payment amount.")
            return

        print("\n1. Cash")
        print("2. Bank Transfer")
        print("3. Card")

        method_choice = input("Choose payment method: ")

        methods = {
            "1": "Cash",
            "2": "Bank Transfer",
            "3": "Card"
        }

        if method_choice not in methods:
            print("Invalid payment method.")
            return

        payment_method = methods[method_choice]

        reference = None

        if payment_method != "Cash":
            reference = f"PAY{random.randint(100000, 999999)}"

        payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        success = add_payment(
            order_id,
            amount,
            payment_method,
            reference,
            payment_date
        )

        if success:
            new_balance = outstanding - amount

            print("\nPayment recorded successfully!")
            print(f"Amount Received: ₦{amount:,}")
            print(f"Remaining Balance: ₦{new_balance:,}")

            if new_balance == 0:
                print("Payment Status: PAID")
            else:
                print("Payment Status: PARTIALLY PAID")

        else:
            print("Unable to record payment.")

    except ValueError:
        print("Please enter a valid number.")

def view_payment_history():
    print("\n--- PAYMENT HISTORY ---")

    try:
        order_id = int(input("Enter Order ID: "))

        order = search_order(order_id)

        if not order:
            print("Order not found.")
            return

        payments = get_order_payments(order_id)

        print(f"\nCustomer: {order[1].title()}")
        print(f"Order Total: ₦{order[2]:,}")
        print(f"Total Paid: ₦{order[7]:,}")
        print(f"Outstanding: ₦{order[2] - order[7]:,}")

        if not payments:
            print("\nNo additional payments recorded.")
            return

        print("\nComplete Payments History:")

        for amount, method, reference, payment_date in payments:
            print("-" * 35)
            print(f"Amount: ₦{amount:,}")
            print(f"Method: {method}")
            print(f"Reference: {reference or 'N/A'}")
            print(f"Date: {payment_date}")

    except ValueError:
        print("Please enter a valid Order ID.")


# Main menu
def main():
    print("\n--- JULIET'S SWEET TREATS ---")
    print("1. New Order")
    print("2. View Order History")
    print("3. Search Order")
    print("4. Delete Order")
    print("5. Edit Order")
    print("6. Exit")
    print("7. Record Additional Payment")
    print("8. View Payment History")

    choice = input("\nChoose an option: ")

    if choice == "1":
        create_order()

    elif choice == "2":
        orders = get_order_history()

        if not orders:
            print("No orders found.")

        else:
            print("\n--- ORDER HISTORY ---")

            previous_order_id = None

            for order in orders:

                (
                    order_id,
                    customer_name,
                    total,
                    amount_paid,
                    payment_method,
                    payment_status,
                    reference,
                    order_date,
                    product_name,
                    quantity,
                    unit_price
                ) = order

                if order_id != previous_order_id:
                    previous_order_id = order_id

                    print("\n------------------------------")
                    print(f"Order ID: {order_id}")
                    print(f"Customer: {customer_name.title()}")
                    print(f"Total: ₦{total:,}")

                    outstanding = max(total - amount_paid, 0)

                    print(f"Amount Paid: ₦{amount_paid:,}")
                    print(f"Outstanding: ₦{outstanding:,}")
                    print(f"Payment: {payment_method}")
                    print(f"Status: {payment_status}")
                    print(f"Date: {order_date}")
                    print("\nItems:")

                if product_name:
                    item_total = quantity * unit_price

                    print(
                        f"  {product_name.title()} x {quantity} "
                        f"= ₦{item_total:,}"
                    )

                else:
                    print("  No product details available for this order.")

    elif choice == "3":
        find_order()

    elif choice == "4":
        remove_order()

    elif choice == "5":
        edit_order()

    elif choice == "6":
        print("Thank you for using Juliet's Sweet Treats!")
        return

    elif choice == "7":
        record_additional_payment()

    elif choice == "8":
        view_payment_history()

    else:
        print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()