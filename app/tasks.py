
from app.celery_worker import celery_app
from app.database import SessionLocal
from app.models import Monitor, HealthCheck
from app.monitoring import check_website
from app.incident_service import process_monitor_check

@celery_app.task
def test_task():
    return "PulseCheck background task executed successfully!"


@celery_app.task
def check_all_monitors():

    db = SessionLocal()

    try:
        # 1. Fetch all active monitors
        monitors = db.query(Monitor).filter(
            Monitor.is_active == True
        ).all()

        checked_count = 0

        # 2. Check each monitor
        for monitor in monitors:

            try:
                result = check_website(monitor.url)

                # Save health check and process incident logic
                process_monitor_check(db, monitor, result)

                checked_count += 1

            except Exception as e:
                db.rollback()
                print(f"Error checking {monitor.name}: {e}")

        return {
            "message": "Monitoring completed",
            "total_monitors": len(monitors),
            "checked_monitors": checked_count
        }

    finally:
        db.close()