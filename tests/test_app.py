import pytest
from server.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_all_inventory(client):
    res = client.get("/inventory")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)



def test_get_single_item_success(client):
    res = client.get("/inventory/1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == 1


def test_get_single_item_not_found(client):
    res = client.get("/inventory/999")
    assert res.status_code == 404
    assert "error" in res.get_json()


def test_add_item(client):
    payload = {
        "product_name": "Test Product",
        "brands": "Test Brand",
        "quantity": 10,
        "price": 5.5
    }

    res = client.post("/inventory", json=payload)
    assert res.status_code == 201

    data = res.get_json()
    assert data["product_name"] == "Test Product"


def test_update_item(client):
    res = client.patch("/inventory/1", json={"price": 99.99})
    assert res.status_code == 200

    updated = client.get("/inventory/1").get_json()
    assert updated["price"] == 99.99


def test_delete_item(client):
    res = client.delete("/inventory/1")
    assert res.status_code == 200

    res_check = client.get("/inventory/1")
    assert res_check.status_code == 404


def test_search_requires_params(client):
    res = client.get("/search")
    assert res.status_code == 400


def test_import_requires_data(client):
    res = client.post("/inventory/import", json={})
    assert res.status_code == 400