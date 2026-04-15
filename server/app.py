from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

inventory = [
    {"id": 1, "product_name": "Milk", "price": 2.5, "quantity": 10},
    {"id": 2, "product_name": "Bread", "price": 1.5, "quantity": 20},
]

next_id = 3


def find_item(item_id):
    return next((item for item in inventory if item["id"] == item_id), None)


@app.route("/")
def home():
    return jsonify({"message": "Inventory API running"}), 200


# GET ALL
@app.route("/inventory", methods=["GET"])
def get_all():
    return jsonify(inventory), 200


# GET ONE
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_one(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


# ADD
@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id
    data = request.get_json()

    if not data or "product_name" not in data:
        return jsonify({"error": "product_name required"}), 400

    new_item = {
        "id": next_id,
        "product_name": data["product_name"],
        "price": data.get("price", 0),
        "quantity": data.get("quantity", 0),
    }

    inventory.append(new_item)
    next_id += 1

    return jsonify(new_item), 201


# UPDATE
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json() or {}

    if "price" in data:
        item["price"] = data["price"]
    if "quantity" in data:
        item["quantity"] = data["quantity"]

    return jsonify(item), 200


# DELETE
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": "Item deleted"}), 200


# SEARCH 
@app.route("/search", methods=["GET"])
def search():
    barcode = request.args.get("barcode")
    query = request.args.get("query")

    if not barcode and not query:
        return jsonify({"error": "Provide barcode or query"}), 400

    return jsonify({"message": "search works"}), 200


@app.route("/inventory/import", methods=["POST"])
def import_item():
    data = request.get_json() or {}

    barcode = data.get("barcode")
    query = data.get("query")

    if not barcode and not query:
        return jsonify({"error": "Provide barcode or query"}), 400

    return jsonify({"message": "import works"}), 201



if __name__ == "__main__":
    app.run(debug=True)