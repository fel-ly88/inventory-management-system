from flask import Flask, jsonify, request
from flask_cors import CORS
import requests as req

app = Flask(__name__)
CORS(app)

# In-memory database

inventory = [
    {"id": 1, "product_name": "Apple", "brands": "FreshFarms", "quantity": 50, "price": 0.99},
    {"id": 2, "product_name": "Milk", "brands": "DairyBest", "quantity": 20, "price": 1.49},
]
next_id = 3  # Auto-incrementing ID counter


# Helper

def find_item(item_id):
    return next((item for item in inventory if item["id"] == item_id), None)

# Routes


# GET /inventory — Return all items
@app.route("/inventory", methods=["GET"])
def get_all():
    return jsonify(inventory), 200


# GET /inventory/<id> — Return a single item
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_one(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
    return jsonify(item), 200


# POST /inventory — Add a new item
@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id
    data = request.get_json()

    if not data or "product_name" not in data:
        return jsonify({"error": "product_name is required"}), 400

    new_item = {
        "id": next_id,
        "product_name": data.get("product_name"),
        "brands": data.get("brands", "Unknown"),
        "quantity": data.get("quantity", 0),
        "price": data.get("price", 0.0),
    }
    inventory.append(new_item)
    next_id += 1
    return jsonify(new_item), 201


# PATCH /inventory/<id> — Update price and/or quantity
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404

    data = request.get_json()
    if "price" in data:
        item["price"] = data["price"]
    if "quantity" in data:
        item["quantity"] = data["quantity"]

    return jsonify(item), 200


# DELETE /inventory/<id> — Remove an item
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global inventory
    item = find_item(item_id)
    if not item:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404

    inventory = [i for i in inventory if i["id"] != item_id]
    return jsonify({"message": f"Item {item_id} deleted successfully"}), 200


# GET /search?name=<query> — Search items by product name
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("name")
    if not query:
        return jsonify({"error": "Query parameter 'name' is required"}), 400

    results = [i for i in inventory if query.lower() in i["product_name"].lower()]
    return jsonify(results), 200


# POST /inventory/import — Import product from OpenFoodFacts API
@app.route("/inventory/import", methods=["POST"])
def import_product():
    global next_id
    data = request.get_json()

    if not data or "barcode" not in data:
        return jsonify({"error": "A 'barcode' field is required to import a product"}), 400

    barcode = data["barcode"]
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    try:
        response = req.get(url, timeout=5)
        product_data = response.json()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch from OpenFoodFacts: {str(e)}"}), 502

    if product_data.get("status") != 1:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404

    product = product_data["product"]
    new_item = {
        "id": next_id,
        "product_name": product.get("product_name", "Unknown"),
        "brands": product.get("brands", "Unknown"),
        "quantity": data.get("quantity", 1),
        "price": data.get("price", 0.0),
    }
    inventory.append(new_item)
    next_id += 1
    return jsonify(new_item), 201


# Run

if __name__ == "__main__":
    app.run(debug=True, port=5000)