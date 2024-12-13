import pytest
from fastapi.testclient import TestClient
from main import app, SessionLocal, Order, OrderStatus

client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    db = SessionLocal()
    yield db
    db.query(Order).delete()
    db.commit()
    db.close()

def test_create_order(test_db):
    order_data = {
        "customer_name": "John Doe",
        "total_amount": 100.0,
        "currency": "EUR"
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["customer_name"] == "John Doe"
    assert response_data["total_amount"] == 100.0
    assert response_data["currency"] == "EUR"

def test_update_order_status(test_db):
    order_data = {
        "customer_name": "John Doe",
        "total_amount": 100.0,
        "currency": "EUR"
    }
    create_response = client.post("/orders/", json=order_data)
    order_id = create_response.json()["id"]

    update_data = {
        "status": "shipped"
    }
    response = client.put(f"/orders/{order_id}/", json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "shipped"

def test_get_order(test_db):
    order_data = {
        "customer_name": "John Doe",
        "total_amount": 100.0,
        "currency": "EUR"
    }
    create_response = client.post("/orders/", json=order_data)
    order_id = create_response.json()["id"]

    response = client.get(f"/orders/{order_id}/")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == order_id

def test_list_orders(test_db):
    order_data_1 = {
        "customer_name": "John Doe",
        "total_amount": 100.0,
        "currency": "EUR"
    }
    order_data_2 = {
        "customer_name": "Jane Doe",
        "total_amount": 200.0,
        "currency": "USD"
    }
    client.post("/orders/", json=order_data_1)
    client.post("/orders/", json=order_data_2)

    response = client.get("/orders/")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
