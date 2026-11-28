
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database import Base


class Monitor(Base):
    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    health_checks = relationship(
    "HealthCheck",
    back_populates="monitor",
    cascade="all, delete-orphan"
)



class HealthCheck(Base):
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True, index=True)

    monitor_id = Column(
        Integer,
        ForeignKey("monitors.id", ondelete="CASCADE"),
        nullable=True
    )

    status_code = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)
    is_success = Column(Boolean, default=False, nullable=True)
    checked_at = Column(DateTime, server_default=func.now())

    monitor = relationship("Monitor", back_populates="health_checks")



class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    monitor_id = Column(
        Integer,
        ForeignKey("monitors.id", ondelete="CASCADE"),
        nullable=False
    )

    started_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)

    is_resolved = Column(Boolean, default=False)