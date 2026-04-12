import sys
import requests

BASE_URL = "http://localhost:5000"

def print_header():
    print("\n" + "=" * 55)
    print("   -------- Inventory Management System ---------")
    print("="*55)
    
def print_menu():
    print("\n  [1] View all inventory")
    print("  [2] View single item")
    print("  [3] Add new item manually")
    print("  [4] Update item (price / quantity)")
    print("  [5] Delete item")
    print("  [6] Search OpenFoodFacts by barcode")
    print("  [7] Search OpenFoodFacts by name")
    print("  [8] Import product from OpenFoodFacts into inventory")
    print("  [0] Exit")
    print()
    
    
def print_item(item):
    print(f"\n  -----ID: {item['id']} -----------")
    print(f"  │  Name      : {item['product_name']}")
    print(f"  │  Brand     : {item['brands']}")
    print(f"  │  Category  : {item['category']}")
    print(f"  │  Barcode   : {item['barcode']}")
    print(f"  │  Quantity  : {item['quantity']}")
    print(f"  │  Price     : ${item['price']:.2f}")
    if item.get("ingredients_text"):
        ingredients = item["ingredients_text"][:60] + ("…" if len(item["ingredients_text"]) > 60 else "")
        print(f"  │  Ingred.   : {ingredients}")
    print(f"  -----------------------------------------")

def print_success(msg):
     print(f"\n Success: {msg}")

def print_error(msg):
    print(f"\n Error: {msg}")
     
def view_all():
 try:
        res = requests.get(f"{BASE_URL}/inventory")
        items = res.json()
        if not items:
            print("\n  No items in inventory.")
            return
        print(f"\n  Found {len(items)} item(s):")
        for item in items:
            print_item(item)
 except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Is Flask running on port 5000?")


def view_single():
        item_id = input("  Enter item ID: ").strip()
        if not item_id.isdigit():
            print_error("ID must be a number.")
            return
        try:
            res = requests.get(f"{BASE_URL}/inventory/{item_id}")
            if res.status_code == 200:
                print_item(res.json())
            else:
                print_error(res.json().get("error", "Item not found."))
        except requests.exceptions.ConnectionError:
            print_error("Cannot connect to server.")
            


def add_item():
    print("\n  Enter new item details:")
    name = input("  Product name (required): ").strip()
    if not name:
        print_error("Product name is required.")
        return

    brand     = input("  Brand: ").strip() or "Unknown"
    barcode   = input("  Barcode: ").strip()
    category  = input("  Category: ").strip() or "General"

    qty = input("  Quantity [0]: ").strip()
    quantity = int(qty) if qty.isdigit() else 0

    price_str = input("  Price [0.00]: ").strip()
    try:
        price = float(price_str) if price_str else 0.0
    except ValueError:
        price = 0.0

    ingredients = input("  Ingredients (optional): ").strip()

    payload = {
        "product_name": name,
        "brands": brand,
        "barcode": barcode,
        "category": category,
        "quantity": quantity,
        "price": price,
        "ingredients_text": ingredients,
    }

    try:
        res = requests.post(f"{BASE_URL}/inventory", json=payload)
        if res.status_code == 201:
            print_success(f"Added '{name}' with ID {res.json()['id']}")
        else:
            print_error(res.json().get("error", "Failed to add item."))
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server.")


def update_item():
    item_id = input("  Enter item ID to update: ").strip()
    if not item_id.isdigit():
        print_error("ID must be a number.")
        return

    print("  Leave blank to keep current value.")
    qty       = input("  New quantity: ").strip()
    price_str = input("  New price: ").strip()

    payload = {}
    if qty.isdigit():
        payload["quantity"] = int(qty)
    if price_str:
        try:
            payload["price"] = float(price_str)
        except ValueError:
            print_error("Invalid price.")
            return

    if not payload:
        print_error("No changes provided.")
        return

    try:
        res = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=payload)
        if res.status_code == 200:
            print_success("Item updated successfully.")
            print_item(res.json())
        else:
            print_error(res.json().get("error", "Update failed."))
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server.")


def delete_item():
    item_id = input("  Enter item ID to delete: ").strip()
    if not item_id.isdigit():
        print_error("ID must be a number.")
        return

    confirm = input(f"  Delete item {item_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    try:
        res = requests.delete(f"{BASE_URL}/inventory/{item_id}")
        if res.status_code == 200:
            print_success(res.json().get("message", "Deleted."))
        else:
            print_error(res.json().get("error", "Delete failed."))
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server.")


def search_by_barcode():
    barcode = input("  Enter barcode: ").strip()
    if not barcode:
        print_error("Barcode is required.")
        return
    try:
        res = requests.get(f"{BASE_URL}/search", params={"barcode": barcode})
        if res.status_code == 200:
            p = res.json()
            print(f"\n  Found on OpenFoodFacts:")
            print(f"  Name       : {p.get('product_name')}")
            print(f"  Brand      : {p.get('brands')}")
            print(f"  Category   : {p.get('category')}")
            print(f"  Barcode    : {p.get('barcode')}")
            ingredients = p.get("ingredients_text", "")[:80]
            if ingredients:
                print(f"  Ingredients: {ingredients}…")
        else:
            print_error("Product not found on OpenFoodFacts.")
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server.")


def search_by_name():
    query = input("  Enter product name: ").strip()
    if not query:
        print_error("Query is required.")
        return
    try:
        res = requests.get(f"{BASE_URL}/search", params={"query": query})
        if res.status_code == 200:
            p = res.json()
            print(f"\n  Found on OpenFoodFacts:")
            print(f"  Name       : {p.get('product_name')}")
            print(f"  Brand      : {p.get('brands')}")
            print(f"  Category   : {p.get('category')}")
            print(f"  Barcode    : {p.get('barcode')}")
        else:
            print_error("Product not found on OpenFoodFacts.")
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server.")


def import_from_api():
    print("\n  Import product from OpenFoodFacts into inventory.")
    barcode = input("  Barcode (or press Enter to search by name): ").strip()
    query = ""
    if not barcode:
        query = input("  Product name: ").strip()

    if not barcode and not query:
        print_error("Provide a barcode or product name.")
        return

    qty = input("  Quantity to stock [1]: ").strip()
    quantity = int(qty) if qty.isdigit() else 1

    price_str = input("  Price [0.00]: ").strip()
    try:
        price = float(price_str) if price_str else 0.0
    except ValueError:
        price = 0.0

    payload = {"quantity": quantity, "price": price}
    if barcode:
        payload["barcode"] = barcode
    else:
        payload["query"] = query

    try:
        res = requests.post(f"{BASE_URL}/inventory/import", json=payload)
        if res.status_code == 201:
            item = res.json()
            print_success(f"Imported '{item['product_name']}' → ID {item['id']}")
            print_item(item)
        else:
            print_error(res.json().get("error", "Import failed."))
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server.")


def main():
    print_header()
    while True:
        print_menu()
        choice = input("  Select option: ").strip()

        if choice == "1":
            view_all()
        elif choice == "2":
            view_single()
        elif choice == "3":
            add_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            search_by_barcode()
        elif choice == "7":
            search_by_name()
        elif choice == "8":
            import_from_api()
        elif choice == "0":
            print("\n  Goodbye! \n")
            sys.exit(0)
        else:
            print_error("Invalid option. Choose 0–8.")


if __name__ == "__main__":
    main()
        
            