# Import FastAPI framework and dependencies for routing and error handling
from fastapi import FastAPI, Depends, HTTPException

# Import Pydantic BaseModel for data validation and EmailStr for email format validation
from pydantic import BaseModel, EmailStr

# Import typing helpers for type hints
from typing import List, Optional

# Import SQLAlchemy core and ORM classes
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Define the SQLite database URL
DB_URL = 'sqlite:///./students.db'

# Create a SQLAlchemy engine connected to the database
engine = create_engine(DB_URL)

# Create a session factory bound to the engine; configure no autocommit or autoflush
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a base class for ORM models
Base = declarative_base()

# Define User model mapped to "users" table in database
class User(Base):
    # Name of the table in DB
    __tablename__ = "users"
    
    # Primary key column, indexed for fast queries
    id = Column(Integer, primary_key=True, index=True)
    
    # User's name, non-nullable column
    name = Column(String, nullable=False)
    
    # User's email, must be unique and indexed, non-nullable
    email = Column(String, unique=True, index=True, nullable=False)

# Create the tables in the database (if they don't exist)
Base.metadata.create_all(bind=engine)

# Define Pydantic model for creating a user (input validation)
class UserCreate(BaseModel):
    # User's name as a string
    name: str
    
    # User's email with email format validation
    email: EmailStr

# Define Pydantic model for user response with ORM compatibility
class UserResponse(BaseModel):
    # User ID
    id: int
    
    # User name
    name: str
    
    # User email
    email: EmailStr

    # Enable compatibility with ORM objects for automatic serialization
    class Config:
        orm_mode = True

# Define Pydantic model for updating user details (optional fields)
class UserUpdate(BaseModel):
    # Optional user name for update
    name: Optional[str] = None
    
    # Optional email for update with email validation
    email: Optional[EmailStr] = None

# Create FastAPI application instance
app = FastAPI()

# Dependency function to provide a database session and ensure closing after use
def get_db():
    # Create a new session from the session factory
    db = SessionLocal()
    try:
        # Yield the session to the path operation function
        yield db
    finally:
        # Ensure the session is closed after request finishes
        db.close()

# Root endpoint to welcome users
@app.get('/')
def welcome():
    # Return simple JSON with name and level
    return {
        "Name": "Ayan Ahmed",
        "Level": "6"
    }

# Endpoint to create a new user
@app.post("/create", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user with the given email already exists in DB
    if db.query(User).filter(User.email == user.email).first():
        # Raise 400 error if email exists
        raise HTTPException(status_code=400, detail='Email already exists')
    # Create new User ORM object
    db_user = User(name=user.name, email=user.email)
    # Add new user to the session
    db.add(db_user)
    # Commit transaction to save user in DB
    db.commit()
    # Refresh the instance to load generated ID
    db.refresh(db_user)
    # Return the newly created user object
    return db_user

# Endpoint to read multiple users with pagination
@app.get("/read", response_model=List[UserResponse])
def read_user(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    # Query DB with offset and limit, return list of users
    return db.query(User).offset(skip).limit(limit).all()

# Endpoint to read single user by user_id
@app.get('/read/{user_id}', response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    # Query user by primary key
    user = db.query(User).filter(User.id == user_id).first()
    # Raise 404 if user not found
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    # Return the found user object
    return user

# Endpoint to update an existing user by ID
@app.put("/update/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    # Fetch user from DB by ID
    user = db.query(User).filter(User.id == user_id).first()
    # Raise 404 if user missing
    if not user:
        raise HTTPException(status_code=404, detail='User not Found')
    # Update name if provided
    if user_in.name is not None:
        user.name = user_in.name
    # Update email if provided, check uniqueness
    if user_in.email is not None:
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(status_code=404, detail='Email already in use')
        user.email = user_in.email
    # Commit changes to DB
    db.commit()
    # Refresh to get latest state
    db.refresh(user)
    # Return updated user object
    return user

# Endpoint to delete a user by ID
@app.delete('/delete/{user_id}')
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Query user to delete
    user = db.query(User).filter(User.id == user_id).first()
    # Raise 404 if user not found
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    # Delete user record
    db.delete(user)
    # Commit deletion
    db.commit()
    # Return deleted user (optional)
    return user
