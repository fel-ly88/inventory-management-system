import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

inventory = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "025293002227",
        "quantity": 50,
        "price": 3.99,
        "category": "Beverages",
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt, sunflower lecithin",
        "image_url": ""
    },
    {
        "id": 2,
        "product_name": "Greek Yoghurt Plain",
        "brands": "Chobani",
        "barcode": "041498000000",
        "quantity": 30,
        "price": 2.49,
        "category": "Dairy",
        "ingredients_text": "Cultured nonfat milk, live and active cultures",
        "image_url": ""
    },
        {
        "id": 3,
        "product_name": "Whole Grain Bread",
        "brands": "Dave's Killer Bread",
        "barcode": "013764400021",
        "quantity": 20,
        "price": 5.49,
        "category": "Bakery",
        "ingredients_text": "Whole wheat flour, water, cane sugar, oats, sunflower seeds",
        "image_url": ""
    },
    {
        "id": 4,
        "product_name": "Peanut Butter Crunchy",
        "brands": "Jif",
        "barcode": "051500756140",
        "quantity": 45,
        "price": 3.79,
        "category": "Spreads",
        "ingredients_text": "Roasted peanuts, sugar, molasses, fully hydrogenated vegetable oils",
        "image_url": "",
    },
    {
        "id": 5,
        "product_name": "Orange Juice",
        "brands": "Tropicana",
        "barcode": "048500202272",
        "quantity": 60,
        "price": 4.29,
        "category": "Beverages",
        "ingredients_text": "100% pure squeezed pasteurized orange juice",
        "image_url": "",
    },
    
]

next_id = 6

def find_item(item_id):
    return next((item for item in inventory if item["id"] == item_id), None)

@app.route("/")
def index():
    return jsonify({"message": "Welcome to the Inventory Management API!"})

@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory),200

@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)
    if item:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
    return jsonify(item), 200

@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id
    data = request.get_json()
    
    if not data or not data.get("product_name"):
        return jsonify({"error": "Missing required field: product_name"}), 400
    
    new_item = {
        "id": next_id,
        "product_name": data["product_name"],
        "brands": data.get("brands", "Unknown"),
        "barcode": data.get("barcode", ""),
        "quantity": data.get("quantity", 0),
        "price": data.get("price", 0.0),
        "category": data.get("category", "General"),
        "ingredients_text": data.get("ingredients_text", ""),
        "image_url": data.get("image_url", "")
    }
    
    inventory.append(new_item)
    next_id +=1
    return jsonify(new_item), 201

@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400
    
    allowed_fields = {"product_name", "brands", "barcode", "quantity", "price", "category", "ingredients_text", "image_url"}
    
    for key, value in data.items():
        if key in allowed_fields:
            item[key] = value
            
    return jsonify(item), 200

@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404

    inventory.remove(item)
    return jsonify({"message": f"Item '{item['product_name']}' deleted successfully"}), 200

 
@app.route("/search", methods=["GET"])
def search_external():
    barcode = requests.args.get("barcode")
    query = request.args.get("query")
    
    if not barcode and not query:
        return jsonify({"error": "Provide 'barcode' or 'query' parameter"}), 400

    result = fetch_from_openfoodfacts(barcode=barcode, query=query)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Product not found in OpenFoodFacts"}), 404

@app.route("/inventory/import", methods=["POST"])
def import_from_api():
    global next_id
    data = request.get_json()
    barcode = data.get("barcode") if data else None
    query = data.get("query") if data else None

    if not barcode and not query:
        return jsonify({"error": "Provide 'barcode' or 'query'"}), 400

    product = fetch_from_openfoodfacts(barcode=barcode, query=query)
    if not product:
        return jsonify({"error": "Product not found in OpenFoodFacts"}), 404

    new_item = {
        "id": next_id,
        "product_name": product.get("product_name", "Unknown"),
        "brands": product.get("brands", "Unknown"),
        "barcode": product.get("barcode", barcode or ""),
        "quantity": data.get("quantity", 1),
        "price": data.get("price", 0.0),
        "category": product.get("category", "General"),
        "ingredients_text": product.get("ingredients_text", ""),
        "image_url": product.get("image_url", ""),
    }

    inventory.append(new_item)
    next_id += 1
    return jsonify(new_item), 201


def fetch_from_openfoodfacts(barcode=None, query=None):
    """
    Fetch product data from OpenFoodFacts API.
    Returns a normalized product dict or None if not found.
    """
    try:
        if barcode:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=5)
            data = response.json()

            if data.get("status") == 1:
                p = data["product"]
                return _normalize_product(p, barcode)

        elif query:
            url = "https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 1,
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()

            products = data.get("products", [])
            if products:
                p = products[0]
                return _normalize_product(p, p.get("code", ""))

    except requests.exceptions.RequestException:
        return None

    return None


def _normalize_product(p, barcode=""):
    """Normalize OpenFoodFacts product dict into our inventory format."""
    categories = p.get("categories_tags", [])
    category = categories[0].replace("en:", "").title() if categories else "General"

    return {
        "product_name": p.get("product_name", "Unknown"),
        "brands": p.get("brands", "Unknown"),
        "barcode": barcode or p.get("code", ""),
        "category": category,
        "ingredients_text": p.get("ingredients_text", ""),
        "image_url": p.get("image_front_url", ""),
    }


if __name__ == "__main__":
    app.run(port=5000, debug=True)