"""
Juliet's Sweet Treats — Bakery Order Calculator

An order calculator supporting multiple items per order, with three
payment methods: Cash, Bank Transfer (simulated USSD flow), and Card.
Run this directly in a terminal (including VS Code's built-in terminal)
with:

    python3 bakery_calculator.py

Note on the bank transfer flow: this SIMULATES what dialing a USSD code
looks like, for demonstration purposes. It does not connect to any real
bank, and never asks for a PIN or real account details — only the USSD
code itself, which is public information (the same code is printed on
the bank's own website). A real production system would need to
integrate with an actual payment gateway (e.g. Paystack, Flutterwave) to
genuinely verify a transfer happened — this simulation cannot do that.
"""

import random
import time
from datetime import datetime

MENU = {
    1: ("vanilla cake", 7000),
    2: ("chocolate cake", 8000),
    3: ("red velvet cake", 9000),
    4: ("doughnut", 500),
    5: ("meat pie", 700),
    6: ("samosa", 500),
    7: ("spring roll", 500),
    8: ("cupcake", 600),
    9: ("buns", 400),
}

# Well-known bank USSD shortcodes (public information — the same codes
# are printed on each bank's own website and posters in their branches).
BANK_USSD_CODES = {
    1: ("GTBank", "*737#"),
    2: ("Access Bank", "*901#"),
    3: ("Zenith Bank", "*966#"),
    4: ("First Bank", "*894#"),
    5: ("UBA", "*919#"),
}

BAKERY_ACCOUNT_NAME = "JULIET'S SWEET TREATS"
# Placeholder account number — replace with the bakery's real account
# number. It's fine for this to be public; account numbers alone can't
# be used to withdraw money, only to receive it.
BAKERY_ACCOUNT_NUMBER = "0123456789"


def print_header():
    print("================================")
    print("       JULIET'S SWEET TREATS")
    print("================================")


def choose_item():
    print_header()
    print("1. Vanilla Cake   - ₦7,000")
    print("2. Chocolate Cake - ₦8,000")
    print("3. Red Velvet Cake - ₦9,000")
    print("4. Doughnut       - ₦500")
    print("5. Meat Pie       - ₦700")
    print("6. Samosa         - ₦500")
    print("7. Spring Roll    - ₦500")
    print("8. Cupcake        - ₦600")
    print("9. Buns           - ₦400")
    print()

    while True:
        try:
            choice = int(input("Choose an item (1-9): "))
            if choice in MENU:
                return MENU[choice]
            print("Please enter a number between 1 and 9.")
        except ValueError:
            print("Please enter a valid number.")


def print_cart_so_far(order_items):
    running_total = sum(subtotal for _, _, _, subtotal in order_items)
    print()
    print("--- Cart so far ---")
    for item, price, quantity, subtotal in order_items:
        print(f"{quantity} x {item} @ ₦{price:,} = ₦{subtotal:,}")
    print("--------------------------------")
    print(f"Running total: ₦{running_total:,}")


def build_order():
    """
    Loops: choose an item, choose a quantity, add it to the order, and
    show the full cart (every item added so far, plus a running total)
    after each addition. If the same item is chosen again, its quantity
    is added to the existing line instead of creating a duplicate one.
    Keeps going until the answer to "add another item?" is no.
    Returns a list of (item_name, price, quantity, subtotal) tuples.
    """
    order_items = []

    while True:
        item, price = choose_item()
        quantity = choose_quantity()

        # Check whether this item is already in the cart.
        existing_index = None
        for i, (existing_item, _, _, _) in enumerate(order_items):
            if existing_item == item:
                existing_index = i
                break

        if existing_index is not None:
            _, _, old_quantity, _ = order_items[existing_index]
            new_quantity = old_quantity + quantity
            new_subtotal = price * new_quantity
            order_items[existing_index] = (item, price, new_quantity, new_subtotal)
            print()
            print(f"Updated: {item} quantity is now {new_quantity} (₦{new_subtotal:,})")
        else:
            subtotal = price * quantity
            order_items.append((item, price, quantity, subtotal))

        print_cart_so_far(order_items)

        while True:
            add_more = input("Add another item? (yes/no): ").strip().lower()
            if add_more in ("yes", "no"):
                break
            print("Please answer yes or no.")

        if add_more == "no":
            break
        print()

    return order_items


def choose_quantity():
    while True:
        try:
            quantity = int(input("Enter quantity: "))
            if quantity > 0:
                return quantity
            print("Quantity must be at least 1.")
        except ValueError:
            print("Please enter a valid number.")


def print_receipt(customer_name, order_items, total, payment_method=None, payment_status=None, change=None):
    print()
    print_header()
    print("Customer:", customer_name)
    print("--------------------------------")
    for item, price, quantity, subtotal in order_items:
        print(f"{quantity} x {item} @ ₦{price:,} = ₦{subtotal:,}")
    print("--------------------------------")
    print(f"TOTAL: ₦{total:,}")
    if payment_method:
        print("Payment Method:", payment_method)
    if payment_status:
        print("Payment Status:", payment_status)
    if change:
        print(f"Change due: ₦{change:,.2f}")
    print("================================")


# --- Receipt file -----------------------------------------------------

def save_receipt_to_txt(customer_name, order_items, total, payment_method, payment_status, reference=None, change=None):
    """
    Writes the final receipt to a .txt file on disk, named using the
    customer's name and the current timestamp (so repeat customers don't
    overwrite each other's receipts).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in customer_name) or "customer"
    filename = f"receipt_{safe_name}_{timestamp}.txt"

    lines = [
        "================================",
        "       JULIET'S SWEET TREATS",
        "================================",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Customer: {customer_name}",
        "--------------------------------",
    ]
    for item, price, quantity, subtotal in order_items:
        lines.append(f"{quantity} x {item} @ ₦{price:,} = ₦{subtotal:,}")
    lines += [
        "--------------------------------",
        f"TOTAL: ₦{total:,}",
        f"Payment Method: {payment_method}",
        f"Payment Status: {payment_status}",
    ]
    if reference:
        lines.append(f"Reference: {reference}")
    if change:
        lines.append(f"Change due: ₦{change:,.2f}")
    lines += [
        "================================",
        "       THANK YOU FOR ORDERING!",
        "================================",
    ]

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return filename


# --- Payment methods -------------------------------------------------

def pay_with_cash(total):
    """Calculates change owed for a cash payment."""
    while True:
        try:
            amount_given = float(input(f"Total due is ₦{total:,}. Enter amount received from customer: ₦"))
        except ValueError:
            print("Please enter a valid amount.")
            continue

        if amount_given < total:
            shortfall = total - amount_given
            print(f"That's ₦{shortfall:,.2f} short of the total. Please collect the remaining amount.")
            continue

        change = amount_given - total
        if change > 0:
            print(f"Change due to customer: ₦{change:,.2f}")
            return "PAID", None, change
        else:
            print("Exact amount received — no change due.")
            return "PAID", None, None


def pay_with_transfer(total):
    """
    Simulates walking through a real USSD menu, step by step, the way it
    would actually appear on a phone screen. This is a SIMULATION for
    demonstration purposes — no real bank is contacted, and nothing here
    can verify money actually moved. A production system needs a real
    payment gateway (e.g. Paystack, Flutterwave) for that.

    Returns (status, reference_number_or_None).
    """
    print()
    print("Bank Transfer selected.")
    print("Which bank is the customer transferring from?")
    for key, (bank_name, code) in BANK_USSD_CODES.items():
        print(f"{key}. {bank_name}")

    while True:
        try:
            bank_choice = int(input("Choose bank (1-5): "))
            if bank_choice in BANK_USSD_CODES:
                break
            print("Please choose a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")

    bank_name, ussd_code = BANK_USSD_CODES[bank_choice]

    print()
    print(f"Dialing {ussd_code} ...")
    time.sleep(1)
    print("Connecting to bank network...")
    time.sleep(1)

    # Step 1: main menu
    while True:
        print()
        print(f"--- {bank_name} Mobile Banking ---")
        print("1. Transfer")
        print("2. Airtime/Data")
        print("3. Balance Enquiry")
        print("0. Exit")
        main_choice = input("Select option: ").strip()
        if main_choice == "1":
            break
        elif main_choice == "0":
            print("Session ended by customer.")
            return "CANCELLED", None, None
        else:
            print("That option isn't relevant right now — please select 1 to Transfer.")

    # Step 2: transfer type
    while True:
        print()
        print("--- Transfer ---")
        print("1. Transfer to Other Bank")
        print("2. Transfer to Same Bank")
        transfer_type = input("Select option: ").strip()
        if transfer_type in ("1", "2"):
            break
        print("Please select 1 or 2.")

    # Step 3: recipient details
    print()
    print(f"Recipient: {BAKERY_ACCOUNT_NAME}")
    entered_account = input(f"Enter account number ({BAKERY_ACCOUNT_NUMBER}): ").strip()

    # Step 4: amount — validated as a real number, same approach as cash
    print()
    while True:
        try:
            entered_amount = float(input(f"Enter amount to transfer (₦{total:,}): "))
            break
        except ValueError:
            print("Please enter a valid amount.")

    # Step 5: confirmation screen
    print()
    print("--- Confirm Transaction ---")
    print(f"Bank:      {bank_name}")
    print(f"Recipient: {BAKERY_ACCOUNT_NAME}")
    print(f"Account:   {entered_account or BAKERY_ACCOUNT_NUMBER}")
    print(f"Amount:    ₦{entered_amount:,.2f}")
    print("1. Confirm")
    print("2. Cancel")

    while True:
        confirm_choice = input("Select option: ").strip()
        if confirm_choice == "1":
            break
        elif confirm_choice == "2":
            print("Transaction cancelled by customer.")
            return "CANCELLED", None, None
        else:
            print("Please select 1 or 2.")

    print()
    print("Processing transaction...")
    time.sleep(1.5)

    # A simulated reference number — this looks like a real bank
    # reference, but is randomly generated and proves nothing on its own.
    reference = f"SIM{random.randint(100000000, 999999999)}"

    print(f"Transaction Successful.")
    print(f"Reference: {reference}")
    print()
    print("IMPORTANT: This reference is SIMULATED, not from a real bank.")
    print("Please confirm the actual alert/credit in the bakery's bank")
    print("account before handing over the order.")

    # Now check the amount actually entered against what's actually owed
    # — this is a separate check from whether the "bank" accepted the
    # transfer. The bank simulation succeeding just means a transfer of
    # SOME amount happened; this checks whether it was the RIGHT amount.
    print()
    if entered_amount < total:
        shortfall = total - entered_amount
        print(f"NOTICE: Amount transferred (₦{entered_amount:,.2f}) is ₦{shortfall:,.2f}")
        print(f"short of the total due (₦{total:,}).")
        print("Transaction declined — insufficient amount. Please ask the")
        print("customer to transfer the remaining balance, or choose a")
        print("different payment method for the shortfall.")
        return f"DECLINED — short by ₦{shortfall:,.2f}", reference, None

    change = entered_amount - total
    if change > 0:
        print(f"Amount transferred (₦{entered_amount:,.2f}) is ₦{change:,.2f} more")
        print(f"than the total due. Change owed to customer: ₦{change:,.2f}")
        return "PENDING — confirm bank alert before releasing order", reference, change

    print("Amount transferred matches the total exactly — no change due.")
    return "PENDING — confirm bank alert before releasing order", reference, None


def pay_with_card(total):
    """
    Simulates a card terminal flow. Like the transfer flow, this does
    NOT process a real card — no card number or PIN is ever requested
    here, since that would require full PCI-compliant infrastructure a
    demo script like this cannot safely provide.
    """
    print()
    print("Card payment selected.")
    print(f"Please process ₦{total:,} on the physical card terminal (POS).")
    input("Press Enter once the terminal shows APPROVED... ")
    confirmed = input("Did the terminal print an APPROVED receipt? (yes/no): ").strip().lower()

    if confirmed == "yes":
        return "PAID", None, None
    else:
        return "DECLINED — try another payment method", None, None


def choose_payment_method(total):
    print()
    print("Payment Methods")
    print("1. Cash")
    print("2. Bank Transfer")
    print("3. Card")

    while True:
        try:
            choice = int(input("Choose payment method (1-3): "))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if choice == 1:
            status, reference, change = pay_with_cash(total)
            return "Cash", status, reference, change
        elif choice == 2:
            status, reference, change = pay_with_transfer(total)
            return "Bank Transfer", status, reference, change
        elif choice == 3:
            status, reference, change = pay_with_card(total)
            return "Card", status, reference, change
        else:
            print("Please choose 1, 2, or 3.")


def main():
    customer_name = input("Enter customer name: ")

    order_items = build_order()
    total = sum(subtotal for _, _, _, subtotal in order_items)

    print_receipt(customer_name, order_items, total)

    payment_method, payment_status, reference, change = choose_payment_method(total)

    print_receipt(customer_name, order_items, total, payment_method, payment_status, change)
    print("       THANK YOU FOR ORDERING!")
    print("================================")

    filename = save_receipt_to_txt(
        customer_name, order_items, total, payment_method, payment_status, reference, change
    )
    print()
    print(f"Receipt saved to: {filename}")


if __name__ == "__main__":
    main()
