# ---------------------- Import Required Libraries ----------------------
from fastapi import FastAPI, Depends, HTTPException   # FastAPI core and dependency tools
from pydantic import BaseModel, EmailStr              # For request validation
from typing import List , Optional
from sqlalchemy import create_engine, Column, Integer, String  # SQLAlchemy core features
from sqlalchemy.orm import declarative_base, sessionmaker, Session  # ORM tools

# ---------------------- Database Configuration ----------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"  # SQLite database file path
engine = create_engine(SQLALCHEMY_DATABASE_URL)    # Create DB engine
SessionLocal = sessionmaker(bind=engine)           # Create local DB session
Base = declarative_base()                          # Base class for ORM models

# ---------------------- User Model Definition ----------------------
class User(Base):
    __tablename__ = "users"                        # Table name in database
    id = Column(Integer, primary_key=True, index=True)  # Primary key column
    name = Column(String, nullable=False)               # User name (required)
    email = Column(String, unique=True, index=True, nullable=False)  # Unique email

# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)

# ---------------------- Pydantic Schema for Request Validation ----------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr  # Ensures a valid email format

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# ---------------------- FastAPI App Initialization ----------------------
app = FastAPI()

# Dependency for DB session management
def get_db():
    db = SessionLocal()
    try:
        yield db   # Provide session to the route
    finally:
        db.close()  # Close connection after request

# ---------------------- Root Endpoint ----------------------
@app.get("/")
def read_root():
    return {"message": "User model ready - v3"}  # Simple test endpoint

# ---------------------- Create User Endpoint ----------------------
@app.post('/users')
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the email already exists in the database
    
    existing = db.query(User).filter(User.email == user.email).first()  # ✅ Added missing ()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user record
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Refresh instance to get new ID
    
    # Return created user data
    return {"id": db_user.id, "name": db_user.name, "email": db_user.email}


@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()