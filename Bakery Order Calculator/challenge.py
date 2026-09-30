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

choice = int(input("Choose an item (1-9): "))

item, price = menu[choice]

print("Item:", item)
print("Price:", price)

quantity = int(input("Enter quantity: "))
total = price * quantity

print("Total: ₦", f"{total:,}")
