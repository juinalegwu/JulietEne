menu = {
    "vanilla cake": 7000,
    "chocolate cake": 8000,
    "red velvet cake": 9000
}
print("JULIET'S SWEET TREATS")
print("1. vanilla cake - 7000")
print("2. chocolate cake - 8000")
print("3. red velvet cake - 9000")

choice = int(input("Choose an item (1-3): "))

if choice == 1:
    item = "vanilla cake"
    price = 7000
elif choice == 2:
    item = "chocolate cake"
    price = 8000
elif choice == 3:
    item = "red velvet cake"
    price = 9000

print(item)
print(price)

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
