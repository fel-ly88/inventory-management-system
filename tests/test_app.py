import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))
import app as flask_app

@pytest.fixture
def client():
    flask_app.app.config["TESTING"] = True

    flask_app.inventory.clear()
    flask_app.inventory.extend([
        {
            "id": 1,
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "barcode": "025293002227",
            "quantity": 50,
            "price": 4.99,
            "category": "Beverages",
            "ingredients_text": "Filtered water, almonds",
            "image_url": "",
        },
        {
            "id": 2,
            "product_name": "Greek Yogurt Plain",
            "brands": "Chobani",
            "barcode": "818290011271",
            "quantity": 30,
            "price": 2.49,
            "category": "Dairy",
            "ingredients_text": "Cultured nonfat milk",
            "image_url": "",
        },
    ])
    flask_app.next_id = 3

    with flask_app.app.test_client() as c:
        yield c


class TestIndexRoute:
    def test_index_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_index_returns_welcome_message(self, client):
        data = client.get("/").get_json()
        assert "Welcome" in data["message"]


class TestGetInventory:
    def test_get_all_returns_200(self, client):
        assert client.get("/inventory").status_code == 200

    def test_get_all_returns_list(self, client):
        assert isinstance(client.get("/inventory").get_json(), list)

    def test_get_all_returns_correct_count(self, client):
        assert len(client.get("/inventory").get_json()) == 2

    def test_items_have_required_fields(self, client):
        for item in client.get("/inventory").get_json():
            assert "id" in item
            assert "product_name" in item
            assert "price" in item
            assert "quantity" in item


class TestGetSingleItem:
    def test_existing_item_returns_200(self, client):
        assert client.get("/inventory/1").status_code == 200

    def test_existing_item_returns_correct_data(self, client):
        data = client.get("/inventory/1").get_json()
        assert data["product_name"] == "Organic Almond Milk"

    def test_nonexistent_item_returns_404(self, client):
        assert client.get("/inventory/999").status_code == 404

    def test_nonexistent_item_returns_error(self, client):
        assert "error" in client.get("/inventory/999").get_json()


class TestPostInventory:
    def test_valid_post_returns_201(self, client):
        res = client.post("/inventory", json={"product_name": "Test", "price": 1.99})
        assert res.status_code == 201

    def test_post_returns_new_item(self, client):
        data = client.post("/inventory", json={"product_name": "Test", "brands": "B"}).get_json()
        assert data["product_name"] == "Test"
        assert "id" in data

    def test_post_missing_name_returns_400(self, client):
        assert client.post("/inventory", json={"brands": "X"}).status_code == 400

    def test_post_empty_body_returns_400(self, client):
        assert client.post("/inventory", json={}).status_code == 400

    def test_post_item_appears_in_inventory(self, client):
        client.post("/inventory", json={"product_name": "Newly Added"})
        names = [i["product_name"] for i in client.get("/inventory").get_json()]
        assert "Newly Added" in names


class TestPatchInventory:
    def test_patch_returns_200(self, client):
        assert client.patch("/inventory/1", json={"price": 6.99}).status_code == 200

    def test_patch_updates_price(self, client):
        client.patch("/inventory/1", json={"price": 9.99})
        assert client.get("/inventory/1").get_json()["price"] == 9.99

    def test_patch_updates_quantity(self, client):
        client.patch("/inventory/1", json={"quantity": 100})
        assert client.get("/inventory/1").get_json()["quantity"] == 100

    def test_patch_nonexistent_returns_404(self, client):
        assert client.patch("/inventory/999", json={"price": 1.0}).status_code == 404

    def test_patch_empty_body_returns_400(self, client):
        assert client.patch("/inventory/1", json={}).status_code == 400


class TestDeleteInventory:
    def test_delete_returns_200(self, client):
        assert client.delete("/inventory/1").status_code == 200

    def test_delete_returns_message(self, client):
        assert "message" in client.delete("/inventory/1").get_json()

    def test_delete_removes_item(self, client):
        client.delete("/inventory/1")
        assert client.get("/inventory/1").status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        assert client.delete("/inventory/999").status_code == 404

    def test_delete_reduces_count(self, client):
        client.delete("/inventory/1")
        assert len(client.get("/inventory").get_json()) == 1


class TestSearchExternal:
    def test_search_no_params_returns_400(self, client):
        assert client.get("/search").status_code == 400

    @patch("app.fetch_from_openfoodfacts")
    def test_search_by_barcode_returns_product(self, mock_fetch, client):
        mock_fetch.return_value = {"product_name": "Mock", "brands": "Brand",
                                   "barcode": "123", "category": "Snacks",
                                   "ingredients_text": "", "image_url": ""}
        assert client.get("/search?barcode=123").status_code == 200

    @patch("app.fetch_from_openfoodfacts")
    def test_search_not_found_returns_404(self, mock_fetch, client):
        mock_fetch.return_value = None
        assert client.get("/search?barcode=000").status_code == 404


class TestImportFromApi:
    @patch("app.fetch_from_openfoodfacts")
    def test_import_returns_201(self, mock_fetch, client):
        mock_fetch.return_value = {"product_name": "Imported", "brands": "B",
                                   "barcode": "111", "category": "X",
                                   "ingredients_text": "", "image_url": ""}
        res = client.post("/inventory/import", json={"barcode": "111", "quantity": 5})
        assert res.status_code == 201

    @patch("app.fetch_from_openfoodfacts")
    def test_import_not_found_returns_404(self, mock_fetch, client):
        mock_fetch.return_value = None
        assert client.post("/inventory/import", json={"barcode": "000"}).status_code == 404

    def test_import_no_params_returns_400(self, client):
        assert client.post("/inventory/import", json={}).status_code == 400


class TestFetchFromOpenFoodFacts:
    @patch("app.requests.get")
    def test_fetch_by_barcode_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            "status": 1,
            "product": {"product_name": "Real Product", "brands": "Brand",
                        "code": "123", "categories_tags": ["en:beverages"],
                        "ingredients_text": "Water", "image_front_url": ""},
        }
        result = flask_app.fetch_from_openfoodfacts(barcode="123")
        assert result["product_name"] == "Real Product"

    @patch("app.requests.get")
    def test_fetch_barcode_not_found(self, mock_get):
        mock_get.return_value.json.return_value = {"status": 0}
        assert flask_app.fetch_from_openfoodfacts(barcode="000") is None

    @patch("app.requests.get")
    def test_fetch_by_query_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            "products": [{"product_name": "Query Result", "brands": "B",
                          "code": "456", "categories_tags": ["en:snacks"],
                          "ingredients_text": "Sugar", "image_front_url": ""}]
        }
        result = flask_app.fetch_from_openfoodfacts(query="snack")
        assert result["product_name"] == "Query Result"

    @patch("app.requests.get")
    def test_fetch_handles_network_error(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.RequestException("error")
        assert flask_app.fetch_from_openfoodfacts(barcode="123") is None

    def test_fetch_no_params_returns_none(self):
        assert flask_app.fetch_from_openfoodfacts() is None
    