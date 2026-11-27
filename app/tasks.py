
from app.celery_worker import celery_app
from app.database import SessionLocal
from app.models import Monitor, HealthCheck
from app.monitoring import check_website


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

                # 3. Create health check record
                new_check = HealthCheck(
                    monitor_id=monitor.id,
                    status_code=result["status_code"],
                    response_time=result["response_time"],
                    is_success=result["is_success"]
                )

                # 4. Save in database
                db.add(new_check)
                db.commit()

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