from fastapi import FastAPI
from app.database import engine

app = FastAPI(
    title = "PulseCheck",
    description = "API Monitoring and Incident Management Platform",
    version = "1.0.0" 
)

@app.get("/")
def home():
    return{
        "message": "Welcome to PulseCheck"
    }

@app.get("/health")
def health_check():
    return{
        "status":"healthy",
        "application": "PulseCheck"
    }

@app.get("/about")
def about():
    return {
        "name": "PulseCheck",
        "description":"An API monitoring and incident management platform",
        "version": "1.0.0"
    }

@app.get("/db-check")
def database_check():
    try:
        with engine.connect() as connection:
            return {"database": "connected"}
    except Exception as e:
        return {"database": "failed", "error": str(e)}