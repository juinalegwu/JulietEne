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
