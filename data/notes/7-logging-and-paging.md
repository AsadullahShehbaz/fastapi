

---

# Pagination, Input Validation, Error Handling, and Logging — Step-by-Step Notes

---

## 1. **Pagination**

### What is pagination?

* It divides the data into smaller chunks (pages) to limit the number of records returned in a single response.
* Common parameters: `skip` (offset), `limit` (number of records per page).

### How to add pagination in FastAPI:

* Use query parameters to receive `skip` and `limit` from the client.
* Pass them to your database query to control the subset of data returned.

### Example:

```python
from typing import List
from fastapi import FastAPI, Query, HTTPException

app = FastAPI()

fake_db = [{"id": i, "name": f"item_{i}"} for i in range(1, 101)]  # Sample data 1 to 100

@app.get("/items/", response_model=List[dict])
def read_items(skip: int = 0, limit: int = 10):
    return fake_db[skip: skip + limit]
```

### Notes:

* Set default values (e.g., `skip=0`, `limit=10`).
* You can enforce max limits for `limit` (e.g., max 50).
* Use FastAPI’s `Query` for extra validation (min/max).

---

## 2. **Input Validation**

### What is input validation?

* Ensures incoming data (path, query, body) matches expected format & constraints.
* Prevents bad data and improves API reliability.

### FastAPI validation tools:

* Pydantic models for JSON body validation.
* Built-in validation for query/path parameters (e.g., types, constraints).
* Use `Query()`, `Path()`, and `Body()` for additional constraints.

### Example with Query validation:

```python
from fastapi import Query

@app.get("/search/")
def search_items(q: str = Query(..., min_length=3, max_length=50)):
    return {"query": q}
```

### Notes:

* `...` means required parameter.
* Use constraints like `min_length`, `max_length`, `gt` (greater than), `le` (less or equal).
* Validate request body using Pydantic models with field types and validators.

---

## 3. **Improved Error Responses**

### What is improved error handling?

* Return clear, consistent, and meaningful error messages and HTTP status codes.
* Helps clients debug issues easier.

### How to do it in FastAPI:

* Use `HTTPException` to return HTTP errors.
* Customize error details.
* Use exception handlers for common errors.

### Example:

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id < 1 or item_id > 100:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
```

### Advanced:

* Create custom exception handlers with `@app.exception_handler()`.
* Validate user input and return `400 Bad Request` if invalid.
* Return `422 Unprocessable Entity` automatically on Pydantic validation errors.

---

## 4. **Basic Logging**

### Why logging?

* Track API requests, errors, and flow for debugging and monitoring.
* Helps in production troubleshooting.

### How to add logging in FastAPI:

* Use Python’s built-in `logging` module.
* Add middleware to log incoming requests and responses.

### Simple example:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response
```

### Notes:

* Configure log format, level (`DEBUG`, `INFO`, `WARNING`, etc.).
* Log important events and errors inside your endpoint functions.
* You can integrate with advanced loggers like `loguru` or external systems later.

---

# Summary

| Feature                  | What to Do                            | FastAPI Tool / Method                          |
| ------------------------ | ------------------------------------- | ---------------------------------------------- |
| Pagination               | Limit/offset queries                  | Query params `skip`, `limit` + slicing         |
| Input Validation         | Validate query/body/path inputs       | Pydantic models + `Query()`, `Path()`          |
| Improved Error Responses | Raise `HTTPException` with clear info | `raise HTTPException(status_code, detail=...)` |
| Basic Logging            | Log requests and responses            | Python `logging` + middleware                  |

---


