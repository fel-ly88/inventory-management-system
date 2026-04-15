import requests
import sys

BASE_URL = "http://localhost:5000"


def show_menu():
    print("\n--- Inventory Menu ---")
    print("1. View all items")
    print("2. View single item")
    print("3. Add item")
    print("4. Update item")
    print("5. Delete item")
    print("0. Exit")


def view_all():
    res = requests.get(f"{BASE_URL}/inventory")
    for item in res.json():
        print(item)


def view_one():
    item_id = input("ID: ")
    res = requests.get(f"{BASE_URL}/inventory/{item_id}")
    print(res.json())


def add_item():
    name = input("Name: ")
    price = float(input("Price: "))
    qty = int(input("Quantity: "))

    data = {"product_name": name, "price": price, "quantity": qty}
    res = requests.post(f"{BASE_URL}/inventory", json=data)
    print(res.json())


def update_item():
    item_id = input("ID: ")
    price = input("New price (leave blank): ")
    qty = input("New quantity (leave blank): ")

    data = {}
    if price:
        data["price"] = float(price)
    if qty:
        data["quantity"] = int(qty)

    res = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=data)
    print(res.json())


def delete_item():
    item_id = input("ID: ")
    res = requests.delete(f"{BASE_URL}/inventory/{item_id}")
    print(res.json())


def main():
    while True:
        show_menu()
        choice = input("Choose: ")

        if choice == "1":
            view_all()
        elif choice == "2":
            view_one()
        elif choice == "3":
            add_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "0":
            sys.exit()
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()