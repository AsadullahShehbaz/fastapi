from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker,Session


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
