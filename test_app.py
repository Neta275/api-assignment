"""
Automated tests for the mock FastAPI service.

Covers:
- Happy flows (200/201)
- Validation errors (400)
- Not found (404)
- Simulated internal server error (500)

Each test is tagged with a TC-XXX ID that corresponds to the test plan.
"""


import pytest
from fastapi.testclient import TestClient
from app import app, item_db

# Test client that simulates HTTP calls to our FastAPI app
client = TestClient(app)


@pytest.fixture(autouse=True) 
def clear_db():
    """
    This fixture runs automatically before each test.
    It makes sure item_db starts empty so tests do not affect each other.
    """
    item_db.clear()


# TC-001 – Health check returns OK
def test_tc001_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# TC-002 – Empty items list
def test_tc002_get_items_empty():
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


# TC-003 – Items list contains data
def test_tc003_get_items_with_data():
    client.post("/items", json={"name": "Apples", "quantity": 3})
    response = client.get("/items")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["name"] == "Apples"
    assert body[0]["quantity"] == 3


# TC-004 – Add first valid item
def test_tc004_add_valid_item():
    payload = {"name": "Apples", "quantity": 3}
    response = client.post("/items", json=payload)

    # depending on configuration, this can be 200 or 201
    assert response.status_code in (200, 201)

    body = response.json()
    assert body["item"]["name"] == "Apples"
    assert body["item"]["quantity"] == 3
    assert body["index"] == 0
    # make sure internal storage is updated
    assert item_db == [{"name": "Apples", "quantity": 3}]


# TC-005 – Add second valid item
def test_tc005_add_second_valid_item():
    client.post("/items", json={"name": "Apples", "quantity": 3})
    response = client.post("/items", json={"name": "Bananas", "quantity": 5})

    assert response.status_code in (200, 201)
    body = response.json()
    assert body["index"] == 1
    assert len(item_db) == 2
    assert item_db[1]["name"] == "Bananas"
    assert item_db[1]["quantity"] == 5


# TC-006 – Missing name field
def test_tc006_missing_name_field():
    response = client.post("/items", json={"quantity": 3})
    assert response.status_code == 400


# TC-007 – Missing quantity field
def test_tc007_missing_quantity_field():
    response = client.post("/items", json={"name": "Apples"})
    assert response.status_code == 400


# TC-008 – Wrong data types
def test_tc008_wrong_data_types():
    response = client.post("/items", json={"name": 123, "quantity": "abc"})
    assert response.status_code == 400


# TC-009 – Empty name
def test_tc009_empty_name():
    response = client.post("/items", json={"name": "", "quantity": 3})
    assert response.status_code == 400
    assert response.json()["detail"] == "Name must not be empty"


# TC-010 – Name contains only spaces
def test_tc010_name_only_spaces():
    response = client.post("/items", json={"name": "   ", "quantity": 3})
    assert response.status_code == 400
    assert response.json()["detail"] == "Name must not be empty"


# TC-011 – Quantity equals 0
def test_tc011_quantity_zero():
    response = client.post("/items", json={"name": "Apples", "quantity": 0})
    assert response.status_code == 400
    assert response.json()["detail"] == "Quantity must be >= 1"


# TC-012 – Negative quantity
def test_tc012_negative_quantity():
    response = client.post("/items", json={"name": "Apples", "quantity": -5})
    assert response.status_code == 400
    assert response.json()["detail"] == "Quantity must be >= 1"

# TC-013 – Invalid / non-JSON body
def test_tc013_invalid_non_json_body():
    
    response = client.post(
        "/items",
        data="this is not json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400

    body = response.json()
    assert body["detail"] == "Invalid request payload"
    assert "errors" in body
    assert isinstance(body["errors"], list)
    assert len(body["errors"]) > 0





# TC-014 – Update existing item at valid index
def test_tc014_update_existing_item():
    # Arrange – add one item at index 0
    client.post("/items", json={"name": "Apples", "quantity": 3})

    # Act – update index 0
    response = client.put("/items/0", json={"name": "Updated", "quantity": 10})

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["index"] == 0
    assert body["item"]["name"] == "Updated"
    assert body["item"]["quantity"] == 10
    # verify internal state
    assert item_db[0] == {"name": "Updated", "quantity": 10}


# TC-015 – Index greater than list length (also covers empty list case)
def test_tc015_update_invalid_index_too_high():
    response = client.put("/items/3", json={"name": "Test", "quantity": 1})
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


# TC-016 – Negative index
def test_tc016_update_negative_index():
    response = client.put("/items/-1", json={"name": "Test", "quantity": 1})
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


# TC-017 – Missing fields in PUT body
def test_tc017_update_missing_fields():
    client.post("/items", json={"name": "Apples", "quantity": 3})
    response = client.put("/items/0", json={"quantity": 5})
    assert response.status_code == 400


# TC-018 – Empty name in PUT
def test_tc018_update_empty_name():
    client.post("/items", json={"name": "Apples", "quantity": 3})
    response = client.put("/items/0", json={"name": "", "quantity": 3})
    assert response.status_code == 400
    assert response.json()["detail"] == "Name must not be empty"


# TC-019 – Quantity < 1 in PUT
def test_tc019_update_quantity_less_than_one():
    client.post("/items", json={"name": "Apples", "quantity": 3})
    response = client.put("/items/0", json={"name": "Apples", "quantity": 0})
    assert response.status_code == 400
    assert response.json()["detail"] == "Quantity must be >= 1"


# TC-020 – Simulated internal server error
def test_tc020_simulated_error():
    response = client.get("/simulate-error")
    assert response.status_code == 500
    assert response.json()["detail"] == "Simulated internal server error"
