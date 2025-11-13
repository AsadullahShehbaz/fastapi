from fastapi import FastAPI,Depends
from database import engine,Base,get_db,Session
import models 
from models import User 

# Define App 
app = FastAPI()

# Create orm model using declarative base & bind with engine 
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI - v1 minimal"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get('/read')
async def read_users(db : Session = Depends(get_db)):
    users = db.query(User).all()
    return users