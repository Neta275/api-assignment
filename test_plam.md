# Test Plan – Mock Items API
## 1. Test Objectives

- Verify that the mock API returns correct responses for:

- Valid requests (happy flows)

- Invalid / malformed requests

- Simulated server errors

- Validate correct HTTP status codes:

  200, 201, 400, 404, 500

- Ensure correct in-memory behavior of item_db = []

- POST /items appends new items

- PUT /items/{index} updates existing items only

- Confirm that FastAPI validation errors (RequestValidationError)
  are mapped from 422 → 400 Bad Request.

## 2. Scope

### In Scope

Functional testing of:

- GET /health

- GET /items

- POST /items

- PUT /items/{index}

- GET /simulate-error

Validation of:

- Payload structure and types

- Business-logic rules

- Status codes and response format

### Out of Scope

- Authentication / authorization

- Performance / load testing

- Data persistence (memory-only)

- Concurrency and race conditions

## 3. Test Environment

- Backend: FastAPI application (app.py)

- Runtime: Python 3.x + virtual environment (venv)

- Execution: uvicorn app:app --reload

### Tools:

- Pytest (automation / CI pipeline)

-Postman or curl (manual testing)

- Base URL:
  http://127.0.0.1:8000

## 4. Test Scenarios & Test Cases
### 4.1 GET /health

- TC-001 – Health check returns OK

   Pre-conditions: Service is running

   Request: GET /health

   Expected:

   Status: 200 OK

   Body: {"status":"ok"}

### 4.2 GET /items — Retrieve all items

- TC-002 – Empty items list

   Pre-conditions: item_db is empty

   Request: GET /items

   Expected:

   Status: 200 OK

   Body: []

- TC-003 – Items list contains data

   Pre-conditions: Items were added via POST /items

   Request: GET /items

   Expected:

   Status: 200 OK

   Body: JSON array with all items in item_db

### 4.3 POST /items — Add new item

- Payload model:

   {"name": "string", "quantity": number}

   Valid Requests

- TC-004 – Add first valid item

   Request Body: {"name":"Apples","quantity":3}

   Expected:

   Status: 201 Created (or 200 OK if configured)

   Item is appended to item_db

   Response contains message, item data, and index

- TC-005 – Add second valid item

   Pre-conditions: At least one item already exists

   Request Body: {"name":"Bananas","quantity":5}

   Expected:

   Status: 201 Created

   Item is appended to item_db

   Index equals previous list length

   Invalid Requests → Expect 400 Bad Request

- TC-006 – Missing name field
- TC-007 – Missing quantity field
- TC-008 – Wrong data types
- TC-009 – Empty name
- TC-010 – name contains only spaces
- TC-011 – quantity = 0
- TC-012 – Negative quantity
- TC-013 – Invalid / non-JSON body

   Expected behavior (all above):

   Status: 400 Bad Request

   Validation errors that would normally return 422
   are mapped to 400

   Business-logic failures (name/quantity rules) also return 400

### 4.4 PUT /items/{index} — Update existing item
Valid Update

- TC-014 – Update existing item at valid index

   Pre-conditions: Item exists at given index

   Request: PUT /items/0
   Body: {"name":"Updated","quantity":10}

   Expected:

   Status: 200 OK

   Item is updated in item_db

   Response contains confirmation and updated item

   Invalid Index → 404 Not Found

- TC-015 – Index greater than list length
- TC-016 – Negative index

   Expected:

   Status: 404 Not Found

   Body: {"detail":"Item not found"}

   Invalid Body → 400 Bad Request

- TC-017 – Missing fields
- TC-018 – Empty name
- TC-019 – quantity < 1

   Expected:

   Status: 400 Bad Request

   Meaningful validation message

### 4.5 GET /simulate-error — Simulated failure

- TC-020 – Simulated internal server error

   Request: GET /simulate-error

   Expected:

   Status: 500 Internal Server Error

   Body: {"detail":"Simulated internal server error"}

## 5. Success Criteria

- All listed test cases pass successfully

- Valid flows return 200 or 201

- Invalid input returns 400

- Non-existing index returns 404

- Only /simulate-error returns 500

- No 422 responses are exposed to the client

### item_db behavior:

- POST = append new item

- PUT = update existing index only

   Same scenarios can be automated in Pytest and executed in CI/CD