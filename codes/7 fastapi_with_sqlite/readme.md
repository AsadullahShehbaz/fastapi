Excellent decision ✅ — learning **CRUD without ORM** first is the perfect way to understand how FastAPI connects to a database at the raw SQL level.

We’ll start simple: **FastAPI + SQLite (using only `sqlite3` library)** — no ORM, no SQLAlchemy yet.
After mastering this, switching to SQLAlchemy will feel *very easy* because you’ll already understand how CRUD logic works.

---

## 🧩 Goal

Create a **FastAPI app** that performs CRUD operations (`Create`, `Read`, `Update`, `Delete`) on a SQLite database using **raw SQL queries**.

---

## 🗂️ Folder Structure

```
fastapi_sqlite_raw/
│
├─ app/
│  ├─ main.py
│  ├─ database.py
│  └─ models.py      # (optional, just for schema reference)
└─ app.db
```

---

## 🪜 Step 1 — Setup

```bash
mkdir fastapi_sqlite_raw
cd fastapi_sqlite_raw
pip install fastapi uvicorn
```

---

## 🪜 Step 2 — Create database connection (`database.py`)

```python
# app/database.py
import sqlite3
from contextlib import contextmanager

DATABASE_URL = "app.db"

@contextmanager
def get_db_connection():
    """Context manager to open & close SQLite connection safely."""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row  # returns dict-like rows
    try:
        yield conn
    finally:
        conn.close()
```

👉 **Explanation:**

* `sqlite3.connect()` connects to the database file.
* `conn.row_factory = sqlite3.Row` allows you to access columns by name (like `row["username"]`).
* `contextmanager` ensures the connection closes automatically after use.

---

## 🪜 Step 3 — Initialize the database (`models.py`)

```python
# app/models.py
import sqlite3

def create_tables():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT
        )
    """)
    conn.commit()
    conn.close()
```

Run this once to create the table:

```bash
python -m app.models
```

---

## 🪜 Step 4 — Main FastAPI app (`main.py`)

```python
# app/main.py
from fastapi import FastAPI, HTTPException
from app.database import get_db_connection
from app.models import create_tables

app = FastAPI(title="FastAPI CRUD without ORM")

# Create tables on startup
@app.on_event("startup")
def startup():
    create_tables()


# 🟢 Create (POST)
@app.post("/users/")
def create_user(username: str, email: str, full_name: str = None):
    with get_db_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, email, full_name) VALUES (?, ?, ?)",
                (username, email, full_name),
            )
            conn.commit()
            return {"message": "User created successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


# 🔵 Read all (GET)
@app.get("/users/")
def read_users():
    with get_db_connection() as conn:
        users = conn.execute("SELECT * FROM users").fetchall()
        return [dict(user) for user in users]


# 🔵 Read single user (GET)
@app.get("/users/{user_id}")
def read_user(user_id: int):
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(user)


# 🟠 Update (PUT)
@app.put("/users/{user_id}")
def update_user(user_id: int, username: str = None, email: str = None, full_name: str = None):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Update only provided fields
        updates = []
        params = []
        if username:
            updates.append("username = ?")
            params.append(username)
        if email:
            updates.append("email = ?")
            params.append(email)
        if full_name:
            updates.append("full_name = ?")
            params.append(full_name)

        if updates:
            params.append(user_id)
            sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cur.execute(sql, tuple(params))
            conn.commit()

        return {"message": "User updated successfully"}


# 🔴 Delete (DELETE)
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
```

---

## 🧠 Key Concepts

| Concept                     | Description                                            |
| --------------------------- | ------------------------------------------------------ |
| `?` placeholders            | Prevent SQL injection; values are bound separately.    |
| `with get_db_connection()`  | Opens & closes DB safely.                              |
| `fetchone()` / `fetchall()` | Used to retrieve query results.                        |
| `dict(user)`                | Converts `sqlite3.Row` object to a normal Python dict. |
| `conn.commit()`             | Saves your changes permanently.                        |

---

## 🚀 Run the app

```bash
uvicorn app.main:app --reload
```

Now visit 👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

You’ll get an automatic **Swagger UI** to test all routes.

---

## 🧪 Example CRUD operations in Swagger

| Action          | Endpoint          | Example Input                                                 |
| --------------- | ----------------- | ------------------------------------------------------------- |
| **Create**      | `POST /users/`    | username=`asad`, email=`asad@test.com`, full_name=`Asadullah` |
| **Read all**    | `GET /users/`     | —                                                             |
| **Read single** | `GET /users/1`    | —                                                             |
| **Update**      | `PUT /users/1`    | full_name=`Asad Creative`                                     |
| **Delete**      | `DELETE /users/1` | —                                                             |

---

## 🧩 What You Learned

* How FastAPI works with SQLite directly
* How to execute and parameterize SQL queries
* How to perform all CRUD operations without ORM
* How to safely manage DB connections

---
