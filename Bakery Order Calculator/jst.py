menu = {
    1: ("vanilla cake", 7000),
    2: ("chocolate cake", 8000),
    3: ("red velvet cake", 9000),
    4: ("doughnut", 500),
    5: ("meat pie", 700),
    6: ("samosa", 500),
    7: ("spring roll", 500),
    8: ("cupcake", 600),
    9: ("buns", 400)
}
print("JULIET'S SWEET TREATS")
print("1. Vanilla Cake - ₦7,000")
print("2. Chocolate Cake - ₦8,000")
print("3. Red Velvet Cake - ₦9,000")
print("4. Doughnut - ₦500")
print("5. Meat Pie - ₦700")
print("6. Samosa - ₦500")
print("7. Spring Roll - ₦500")
print("8. Cupcake - ₦600")
print("9. Buns - ₦400")

choice = int(input("Choose an item (1-9): "))

item, price = menu[choice]

print("Item:", item)
print("Price:", price)


quantity = int(input("Enter quantity: "))
total = price * quantity
print(f"Total: ₦{total:,}")

customer_name = input("Enter customer name: ") 
print("================================")
print("       JULIET'S SWEET TREATS")
print("================================")
print("Customer:", customer_name)
print("Item:", item)
print("Price: ₦", f"{price:,}")
print("Quantity:", quantity)
print("--------------------------------")
print(f"TOTAL: ₦{total:,}")
print("================================")

#payment method
print()
print("Payment Methods")
print("1. Cash")
print("2. Bank Transfer")
print("3. Card")

payment_choice = int(input("Choose payment method (1-3): "))
if payment_choice == 1:
    payment_method = "Cash"
elif payment_choice == 2:
    payment_method = "Bank Transfer"
elif payment_choice == 3:
    payment_method = "Card"
print("Payment Method:", payment_method)

#confirm payment
payment_confirmed = input("Has payment been made? (yes/no): ")
if payment_confirmed.lower() == "yes":
    payment_status = "PAID"
else:
    payment_status = "PENDING"
print("Payment Status:", payment_status)


print()
print("================================")
print("       JULIET'S SWEET TREATS")
print("================================")
print("Customer:", customer_name)
print("Item:", item)
print("Price: ₦", f"{price:,}")
print("Quantity:", quantity)
print("--------------------------------")
print(f"TOTAL: ₦{total:,}")
print("Payment Method:", payment_method)
print("Payment Status:", payment_status)
print("================================")
print("       THANK YOU FOR ORDERING!")
print("================================")
