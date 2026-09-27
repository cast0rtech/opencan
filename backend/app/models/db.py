from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MetricAggregateMinute(Base):
    __tablename__ = "metrics_minute"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inverter_id = Column(String(64), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    avg_power = Column(Float, nullable=False)
    max_power = Column(Float, nullable=False)
    min_power = Column(Float, nullable=False)
    avg_voltage = Column(Float, nullable=False)
    avg_frequency = Column(Float, nullable=False)
    accumulated_energy = Column(Float, nullable=False)
