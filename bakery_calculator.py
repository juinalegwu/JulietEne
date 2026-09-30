import random
import time
from datetime import datetime
from database import get_products, save_order


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


def pay_with_cash(total):
    print("\n--- CASH PAYMENT ---")

    while True:
        try:
            amount = int(input(f"Enter cash amount (₦{total:,}): "))

            if amount < total:
                print("Insufficient cash. Please enter enough money.")
                continue

            change = amount - total

            print(f"Payment received: ₦{amount:,}")
            print(f"Change: ₦{change:,}")

            return "Cash", "PAID", None, change

        except ValueError:
            print("Please enter a valid amount.")


def pay_with_transfer(total):
    print("\n--- BANK TRANSFER ---")
    print("This is a simulated transfer for demonstration only.")

    print(f"\nAmount to transfer: ₦{total:,}")

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

    print("Transfer successful!")

    return "Bank Transfer", "PAID", reference, 0


def pay_with_card(total):
    print("\n--- CARD PAYMENT ---")

    print(f"Amount: ₦{total:,}")

    input("Enter card number: ")
    input("Enter PIN: ")

    print("\nProcessing card payment...")
    time.sleep(2)

    reference = f"CARD{random.randint(100000, 999999)}"

    print("Card payment successful!")

    return "Card", "PAID", reference, 0


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


def print_receipt(
    customer_name,
    orders,
    total,
    payment_method,
    payment_status,
    reference,
    change
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

    print("-" * 50)
    print(f"TOTAL: ₦{total:,}")
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


def main():
    print_header()

    customer_name = input("\nEnter customer name: ")

    orders = build_order()

    if not orders:
        print("No items were ordered.")
        return

    print_cart(orders)

    total = calculate_total(orders)

    payment_method, payment_status, reference, change = choose_payment_method(
        total
    )

    print_receipt(
        customer_name,
        orders,
        total,
        payment_method,
        payment_status,
        reference,
        change
    )


if __name__ == "__main__":
    main()