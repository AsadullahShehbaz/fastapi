
---

I’ll start with **Version 1 → Version 3** (small), then continue in the next message with **Version 4 → Version 8 (mega modular)** so you can test each stage step-by-step.

---

## 🧩 Version 1 — Minimal App

**Goal:** Just learn FastAPI basics.

```
fastapi-users-v1/
├── app/
│   └── main.py
├── requirements.txt
└── README.md
```

### `app/main.py`

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI - v1 minimal"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### `requirements.txt`

```
fastapi
uvicorn
```

**Run:**

```bash
uvicorn app.main:app --reload
```

---

## 🧩 Version 2 — Add Database Engine + Base

**Goal:** Learn SQLAlchemy setup, create engine, `SessionLocal`, and `Base`.

```
fastapi-users-v2/
├── app/
│   ├── main.py
│   └── database.py
├── requirements.txt
└── README.md
```

### `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"

# Needed for SQLite to work with multiple threads in FastAPI
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `app/main.py`

```python
from fastapi import FastAPI
from .database import engine, Base

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Engine ready - v2"}
```

### `requirements.txt`

```
fastapi
uvicorn
sqlalchemy
```

**Run:**

```bash
uvicorn app.main:app --reload
```

**Practice:**

* Try importing `get_db()` in `main.py` to confirm import works.
* Open `users.db` file after running; it should be empty but created.

---

## 🧩 Version 3 — Add User Model

**Goal:** Create a `User` SQLAlchemy model and create tables.

```
fastapi-users-v3/
├── app/
│   ├── main.py
│   ├── database.py
│   └── models.py
├── requirements.txt
└── README.md
```

### `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `app/models.py`

```python
from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
```

### `app/main.py`

```python
from fastapi import FastAPI
from . import models
from .database import engine

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "User model ready - v3"}
```

### `requirements.txt`

```
fastapi
uvicorn
sqlalchemy
```

**Run:**

```bash
uvicorn app.main:app --reload
```

**Practice:**

* Start Python shell:

  ```python
  from app.database import SessionLocal
  from app.models import User
  db = SessionLocal()
  db.add(User(name="Alice", email="alice@example.com"))
  db.commit()
  print(db.query(User).all())
  db.close()
  ```
* Inspect `users.db` — now contains a `users` table!

---


Fantastic — below are **Versions 4 → 8 (mega)** with **complete working code for every file** in each version’s folder. Each version is runnable independently. I included `requirements.txt` and a quick run command for each version. I kept comments in the code so you can learn what's happening.

---

## Version 4 — `v4_create_user_route`

**Goal:** Pydantic schemas + `POST /users` to create users via API.

```
fastapi-users-v4/
├── app/
│   └── v4_create_user_route.py
├── users.db
└── requirements.txt
```

### `app/v4_create_user_route.py`

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

app = FastAPI(title="FastAPI Users v4")

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

### `requirements.txt`

```
fastapi
uvicorn
sqlalchemy
pydantic
```

**Run**

```bash
uvicorn app.v4_create_user_route:app --reload
# then open http://127.0.0.1:8000/docs
```

**Practice**

* Create users via Swagger UI.
* Add a `GET /users/{id}` route (exercise).

---

## Version 5 — `v5_full_crud`

**Goal:** Full CRUD routes with response models and `orm_mode`.

```
fastapi-users-v5/
├── app/
│   └── v5_full_crud.py
├── users.db
├── tests/
│   └── test_users.py    # optional starting point
└── requirements.txt
```

### `app/v5_full_crud.py`

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

# SQLAlchemy model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

Base.metadata.create_all(bind=engine)

# Pydantic schemas
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

app = FastAPI(title="FastAPI Users v5")

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
        exists = db.query(User).filter(User.email == user_in.email).first()
        if exists and exists.id != user_id:
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

### `requirements.txt`

```
fastapi
uvicorn
sqlalchemy
pydantic
pytest
```

**Run**

```bash
uvicorn app.v5_full_crud:app --reload
```

**Practice**

* Write tests using `TestClient` to validate endpoints.
* Add search by email query param.

---

## Version 6 — `v6_auth_hashing`

**Goal:** Add password hashing with `passlib` and a basic `/login` endpoint.

```
fastapi-users-v6/
├── app/
│   └── v6_auth_hashing.py
├── users.db
└── requirements.txt
```

### `app/v6_auth_hashing.py`

```python
# v6_auth_hashing.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
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

# Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config:
        orm_mode = True

class LoginIn(BaseModel):
    email: EmailStr
    password: str

app = FastAPI(title="FastAPI Users v6")

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

@app.post("/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(name=user.name, email=user.email, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login/")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # In v6 we do not return JWT — just return basic user info for now
    return {"id": user.id, "email": user.email, "name": user.name}
```

### `requirements.txt`

```
fastapi
uvicorn
sqlalchemy
passlib[bcrypt]
pydantic
```

**Run**

```bash
uvicorn app.v6_auth_hashing:app --reload
```

**Practice**

* Create a user and confirm hashed password stored in `users.db`.
* Try logging in with correct and incorrect passwords.

---

## Version 7 — `v7_pagination_validation`

**Goal:** Add pagination validation, custom request validation errors, and basic logging.

```
fastapi-users-v7/
├── app/
│   └── v7_pagination_validation.py
├── users.db
├── logging.yaml
└── requirements.txt
```

### `app/v7_pagination_validation.py`

```python
# v7_pagination_validation.py
import logging
from logging.config import dictConfig
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext

# simple logging config
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {"default": {"format": "%(levelname)s:%(name)s:%(message)s"}},
    "handlers": {"default": {"class": "logging.StreamHandler", "formatter": "default"}},
    "root": {"level": "INFO", "handlers": ["default"]},
}
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("fastapi-users-v7")

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

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

app = FastAPI(title="FastAPI Users v7")

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

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Return a tidy JSON structure for validation errors
    logger.warning("Validation error for request %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "detail": exc.errors(),
            "body": exc.body,
        },
    )

@app.post("/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(name=user.name, email=user.email, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("Created user %s (id=%s)", db_user.email, db_user.id)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # enforce a maximum limit
    max_limit = 100
    original_limit = limit
    limit = min(limit, max_limit)
    if original_limit != limit:
        logger.info("Limit clamped from %s to %s", original_limit, limit)
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
        exists = db.query(User).filter(User.email == user_in.email).first()
        if exists and exists.id != user_id:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = user_in.email
    db.commit()
    db.refresh(user)
    logger.info("Updated user id=%s", user.id)
    return user

@app.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    logger.info("Deleted user id=%s", user_id)
    return user
```

### `requirements.txt`

```
fastapi
uvicorn
sqlalchemy
passlib[bcrypt]
pydantic
```

**Run**

```bash
uvicorn app.v7_pagination_validation:app --reload
```

**Practice**

* Try `GET /users?limit=1000` and observe the clamped limit behavior.
* Send an invalid request body to see the custom validation error shape.

---

## Version 8 — `v8_mega` (complete modular app with JWT auth)

**Goal:** Full modular app split into files: `database.py`, `models.py`, `schemas.py`, `crud.py`, `auth.py`, `routers/users.py`, `main.py`, `settings.py`. Includes JWT auth to protect user read endpoints.

```
fastapi-users-v8/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── auth.py
│   ├── routers/
│   │   └── users.py
│   └── settings.py
├── users.db
├── requirements.txt
├── Dockerfile            # optional
└── README.md
```

> This v8 is runnable end-to-end. It uses SQLite for simplicity. JWT tokens produced by `/auth/token` are required to access protected endpoints (e.g., `GET /users/`).

---

### `app/settings.py`

```python
# settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # keep a long random secret in production, store in env
    SECRET_KEY: str = "change-this-secret-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./users.db"

    class Config:
        env_file = ".env"

settings = Settings()
```

### `app/database.py`

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `app/models.py`

```python
# models.py
from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
```

### `app/schemas.py`

```python
# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
```

### `app/crud.py`

```python
# crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.User, user_in: schemas.UserUpdate):
    if user_in.name is not None:
        db_user.name = user_in.name
    if user_in.email is not None:
        db_user.email = user_in.email
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: models.User):
    db.delete(db_user)
    db.commit()
    return db_user
```

### `app/auth.py`

```python
# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import crud, schemas
from .database import get_db
from .settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Dependency used to get current user from token, raises 401 on failure
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user
```

> Note: `oauth2_scheme` expects the token endpoint at `/auth/token`.

### `app/routers/users.py`

```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, auth
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.get_password_hash(user_in.password)
    user = crud.create_user(db, user=user_in, hashed_password=hashed)
    return user

@router.get("/", response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    # Protected route — only authenticated users can list users
    limit = min(limit, 100)
    return crud.get_users(db, skip=skip, limit=limit)

@router.get("/me", response_model=schemas.UserResponse)
def read_me(current_user=Depends(auth.get_current_user)):
    # Return the current user's info
    return current_user

@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_in: schemas.UserUpdate, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Optionally: check permissions (only owner or admin)
    updated = crud.update_user(db, db_user, user_in)
    return updated

@router.delete("/{user_id}", response_model=schemas.UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted = crud.delete_user(db, db_user)
    return deleted
```

### `app/main.py`

```python
# main.py
from fastapi import FastAPI, Depends
from .database import engine
from . import models
from .routers import users as users_router
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings

# create DB tables (development only)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Users v8 (modular)")

# CORS (example)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(users_router.router)

# Auth routes (token endpoint)
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from . import auth, schemas
from sqlalchemy.orm import Session
from .database import get_db

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

app.include_router(auth_router)
```

### `requirements.txt`

```
fastapi
uvicorn
sqlalchemy
pydantic
passlib[bcrypt]
python-jose[cryptography]
python-multipart
```

**Run**

```bash
uvicorn app.main:app --reload
# POST to /auth/token with form fields:
#   username=<email>
#   password=<password>
# Use the returned access_token as: Authorization: Bearer <token>
```

**Notes and practice ideas**

1. This modular v8 is production-oriented:

   * `app/settings.py` reads from `.env` via Pydantic `BaseSettings`.
   * `auth.py` uses JWT tokens (python-jose).
2. **Further practice**

   * Swap SQLite for Postgres (update `DATABASE_URL` and Dockerfile).
   * Add Alembic migrations.
   * Add role/permission checks so only admins can delete users.
   * Add tests (use `TestClient`), and a GitHub Actions workflow.
   * Add refresh tokens if desired.

---

## Extra: `Dockerfile` (optional) for v8

Put in repo root (optional):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
```

---

## What I delivered

* **Complete code** for Versions 4 → 8 with every file needed to run.
* v4–v7 are single-file per version (keeps progressive learning simple).
* v8 is **fully modular** and production-like, with JWT auth.

---

