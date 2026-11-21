from fastapi import FastAPI
from app.database import engine
from app.database import engine, Base
from app import models
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Monitor
from app.schemas import MonitorCreate

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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


@app.post("/monitors")
def create_monitor(
    monitor: MonitorCreate,
    db: Session = Depends(get_db)
):
    new_monitor = Monitor(
        name=monitor.name,
        url=str(monitor.url)
    )

    db.add(new_monitor)
    db.commit()
    db.refresh(new_monitor)

    return new_monitor

@app.get("/monitors")
def get_monitors(db: Session = Depends(get_db)):
    monitors = db.query(Monitor).all()
    return monitors

@app.get("/monitors/{monitor_id}")
def get_monitor(monitor_id: int, db: Session = Depends(get_db)):

    monitor = db.query(Monitor).filter(
        Monitor.id == monitor_id
    ).first()

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found"
        )

    return monitor