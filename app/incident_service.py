
from sqlalchemy.orm import Session

from app.models import Monitor, HealthCheck, Incident


def process_monitor_check(db: Session, monitor: Monitor, result: dict):

    # 1. Save the health check
    new_check = HealthCheck(
        monitor_id=monitor.id,
        status_code=result["status_code"],
        response_time=result["response_time"],
        is_success=result["is_success"]
    )

    db.add(new_check)
    db.flush()

    # 2. Find any currently open incident
    open_incident = db.query(Incident).filter(
        Incident.monitor_id == monitor.id,
        Incident.is_resolved == False
    ).first()

    # 3. If the website is working, resolve the incident
    if result["is_success"]:

        if open_incident:
            open_incident.is_resolved = True
            open_incident.resolved_at = new_check.checked_at

    else:
        # 4. Get the latest three health checks
        recent_checks = db.query(HealthCheck).filter(
            HealthCheck.monitor_id == monitor.id
        ).order_by(
            HealthCheck.id.desc()
        ).limit(3).all()

        # 5. Create an incident after three consecutive failures
        if (
            len(recent_checks) == 3
            and all(not check.is_success for check in recent_checks)
            and open_incident is None
        ):
            incident = Incident(
                monitor_id=monitor.id,
                is_resolved=False
            )
            db.add(incident)

    db.commit()
    db.refresh(new_check)

    return new_check
