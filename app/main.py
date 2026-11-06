from fastapi import FastAPI

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