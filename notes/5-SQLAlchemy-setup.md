# FastAPI Users — 8 Progressive Versions (mini → mega)

This document contains **8 incremental versions** of the single-file FastAPI Users app to practise from minimal to production-ready (mega). Each version builds on the previous one. For each version you'll find: **code**, **what changed**, **how to run**, and **practice tasks**.

---

## Version 1 — `v1_minimal.py`

**Goal:** Tiny FastAPI app with one route. Understand `uvicorn` and basic route flow.

```python
# v1_minimal.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI - v1 minimal"}
```

**Run:** `uvicorn v1_minimal:app --reload`

**Practice:** Add `GET /health` returning `status: ok`.

---

## Version 2 — `v2_db_engine_base.py`

**Goal:** Add SQLAlchemy engine, sessionmaker, and `Base`. No models yet. Learn connection string.

```python
# v2_db_engine_base.py
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Engine ready - v2"}
```

**Run:** `uvicorn v2_db_engine_base:app --reload`

**Practice:** Create a dependency `get_db()` that yields a session and closes it.

---

## Version 3 — `v3_user_model.py`

**Goal:** Define a `User` SQLAlchemy model and create tables.

```python
# v3_user_model.py
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "User model ready - v3"}
```

**Run:** `uvicorn v3_user_model:app --reload`

**Practice:** Open Python REPL and use `SessionLocal()` to create and query a `User` row.

---

## Version 4 — `v4_create_user_route.py`

**Goal:** Add Pydantic schemas and `POST /users` to create users via API.

```python
# v4_create_user_route.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    name: str
    email: EmailStr

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "name": db_user.name, "email": db_user.email}
```

**Run:** `uvicorn v4_create_user_route:app --reload`

**Practice:** Use Swagger UI `http://127.0.0.1:8000/docs` to create users.

---

## Version 5 — `v5_full_crud.py`

**Goal:** Full CRUD routes: create, read all, read by id, update, delete. Add response models.

```python
# v5_full_crud.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_in.name is not None:
        user.name = user_in.name
    if user_in.email is not None:
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = user_in.email
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user
```

**Run:** `uvicorn v5_full_crud:app --reload`

**Practice:** Add unit tests using `TestClient` to verify endpoints.

---

## Version 6 — `v6_auth_hashing.py`

**Goal:** Add password hashing with `passlib` and a simple `/login` endpoint (no JWT yet). Store `hashed_password`.

```python
# v6_auth_hashing.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

@app.post("/users/", status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(name=user.name, email=user.email, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "name": db_user.name, "email": db_user.email}

@app.post("/login/")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"id": user.id, "email": user.email, "name": user.name}
```

**Run:** `uvicorn v6_auth_hashing:app --reload`

**Practice:** Attempt login with correct & incorrect passwords; inspect DB file to confirm hashed password.

---

## Version 7 — `v7_pagination_validation.py`

**Goal:** Add pagination, input validation, improved error responses, and basic logging.

Key changes:

* Add `skip`/`limit` to list users (already present in v5 but now with validation).
* Use `limit` max clamp to 100.
* Add `logging` statements and structured error messages.

**Practice:** Introduce `fastapi.exceptions.RequestValidationError` handling to return custom JSON errors.

---

## Version 8 (Mega) — `v8_mega.py`

**Goal:** Production-style single file with:

* Dependency `get_db`
* CRUD functions separated from route handlers
* Password hashing + login
* Response models + validation
* CORS (optional), simple settings via `pydantic` `BaseSettings`
* Notes for Alembic, Dockerfile, and JWT integration (snippets)

> This mega file combines everything you've practised. Use it to understand the full workflow before splitting into modules.

**Practice tasks for mega:**

1. Split the mega file into modules: `database.py`, `models.py`, `schemas.py`, `crud.py`, `main.py`.
2. Add Alembic and create initial migration.
3. Implement JWT auth and protect `/users` endpoints.
4. Write pytest tests for all endpoints and CI using GitHub Actions.

---

# How to Practise (Suggested progression)

1. Start with **v1**, run it, and add the tiny health endpoint.
2. Move to **v2**, implement `get_db()` dependency.
3. Continue to **v3** and inspect DB file after `create_all()` runs.
4. Use **v4** to learn request validation and how Swagger generates a form.
5. Use **v5** to learn full CRUD behavior and response models (`orm_mode`).
6. Use **v6** to learn hashing and login flow.
7. Use **v7** for validation & logging improvements.
8. Finish with **v8** (mega) and then **refactor** into modules and add Alembic/JWT.

# Tips & Best Practices

* Always close DB sessions.
* Never store plain-text passwords.
* Use Alembic for migrations in real projects.
* Write tests and CI early.
* Use environment variables for secrets (do not hardcode DB credentials).

---

