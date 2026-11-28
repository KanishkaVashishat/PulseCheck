from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.incident_service import process_monitor_check
from app.database import engine, Base, SessionLocal
from app import models
from app.models import Monitor, HealthCheck
from app.schemas import (
    MonitorCreate,
    MonitorResponse,
    HealthCheckResponse
)
from app.monitoring import check_website

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def send_notification(monitor_name, status_code):
    print(f"Monitor: {monitor_name}")
    print(f"Status: {status_code}")
    print("Website monitoring completed!")

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

@app.get("/monitors", response_model=list[MonitorResponse])
def get_monitors(db: Session = Depends(get_db)):
    return db.query(Monitor).all()

@app.get("/monitors/{monitor_id}",response_model=MonitorResponse)
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

@app.post("/monitors/{monitor_id}/check")
def run_monitor_check(
    monitor_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # 1. Find monitor in database
    monitor = db.query(Monitor).filter(
        Monitor.id == monitor_id
    ).first()

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found"
        )

    # 2. Check the website
    result = check_website(monitor.url)
    background_tasks.add_task(
    send_notification,
    monitor.name,
    result["status_code"]
    )

    # 3. Create health check record
    new_check = process_monitor_check(db, monitor, result)
        

    # 5. Return result
    return {
        "monitor": monitor.name,
        "url": monitor.url,
        "status_code": new_check.status_code,
        "response_time": new_check.response_time,
        "is_success": new_check.is_success
    }


@app.get(
    "/monitors/{monitor_id}/checks",
    response_model=list[HealthCheckResponse]
)
def get_monitor_checks(
    monitor_id: int,
    db: Session = Depends(get_db)
):
    monitor = db.query(Monitor).filter(
        Monitor.id == monitor_id
    ).first()

    if monitor is None:
        raise HTTPException(status_code=404, detail="Monitor not found")

    checks = db.query(HealthCheck).filter(
        HealthCheck.monitor_id == monitor_id
    ).order_by(HealthCheck.checked_at.desc()).all()

    return checks


@app.get("/monitors/{monitor_id}/stats")
def get_monitor_stats(
    monitor_id: int,
    db: Session = Depends(get_db)
):
    monitor = db.query(Monitor).filter(
        Monitor.id == monitor_id
    ).first()

    if monitor is None:
        raise HTTPException(status_code=404, detail="Monitor not found")

    checks = db.query(HealthCheck).filter(
        HealthCheck.monitor_id == monitor_id
    ).all()

    total_checks = len(checks)

    successful_checks = sum(
        1 for check in checks if check.is_success
    )

    failed_checks = total_checks - successful_checks

    uptime_percentage = (
        successful_checks / total_checks * 100
        if total_checks > 0 else 0
    )

    response_times = [
        check.response_time
        for check in checks
        if check.response_time is not None
    ]

    avg_response_time = (
        sum(response_times) / len(response_times)
        if response_times else 0
    )

    return {
        "monitor": monitor.name,
        "total_checks": total_checks,
        "successful_checks": successful_checks,
        "failed_checks": failed_checks,
        "uptime_percentage": round(uptime_percentage, 2),
        "average_response_time": round(avg_response_time, 2)
    }

@app.get("/test-background")
def test_background(background_tasks: BackgroundTasks):

    background_tasks.add_task(
    send_notification,
    "Google",
    200
    )

    return {
        "message": "Response sent! Background task is running."
    }