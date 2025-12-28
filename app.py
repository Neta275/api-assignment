# Mock API service used for testing behavior and validation scenarios.
# Data is stored in-memory (item_db) because the goal is to simulate API behavior,
# not persistence or production storage.

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Data model for incoming item payloads
class Item(BaseModel):
    name: str
    quantity: int


# In-memory storage – used only for testing behavior (no database)
item_db = []


# Convert FastAPI validation errors (normally 422) into HTTP 400,
# to match the exercise requirements and provide consistent responses.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid request payload", "errors": exc.errors()},
    )


# Health-check endpoint – verifies that the service is running
@app.get("/health")
def get_health():
    return {"status": "ok"}


# Returns the full list of items (collection endpoint)
# Even if the list is empty – response is still 200 OK
@app.get("/items")
def get_items():
    return item_db


# Adds a new item to the list
# POST = create resource. Returns 201 Created (or 200 if configured).
@app.post("/items", status_code=201)
def post_item(item: Item):

    # Business-logic validation (not only schema validation)
    if not item.name or not item.name.strip():
        raise HTTPException(status_code=400, detail="Name must not be empty")

    if item.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be >= 1")

    record = {"name": item.name, "quantity": item.quantity}
    item_db.append(record)

    return {"message": "item added", "item": record, "index": len(item_db) - 1}


# Updates an existing item by index.
# Important: PUT does NOT create new items.
# If the index does not exist → return 404 by design.
@app.put("/items/{index}")
def put_item(index: int, item: Item):

    if index < 0 or index >= len(item_db):
        raise HTTPException(status_code=404, detail="Item not found")

    if not item.name or not item.name.strip():
        raise HTTPException(status_code=400, detail="Name must not be empty")

    if item.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be >= 1")

    updated = {"name": item.name, "quantity": item.quantity}
    item_db[index] = updated

    return {"message": "item updated", "index": index, "item": updated}


# Endpoint used only to simulate a server failure scenario (500 error)
@app.get("/simulate-error")
def simulate_error():
    raise HTTPException(status_code=500, detail="Simulated internal server error")
