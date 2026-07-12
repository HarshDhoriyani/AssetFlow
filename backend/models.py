from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    asset_code = Column(String, unique=True, index=True)
    category = Column(String)
    state = Column(String, default="active") # active, allocated, maintenance, retired
    purchase_value = Column(Float, default=0.0)
    current_location = Column(String)
    assigned_to = Column(String)
    health_score = Column(Float, default=100.0)
    risk_level = Column(String, default="low") # low, medium, high, critical
    image_url = Column(String, nullable=True)

    maintenance_requests = relationship("MaintenanceRequest", back_populates="asset")
    predictions = relationship("Prediction", back_populates="asset")

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    requested_by = Column(String)
    assigned_to = Column(String)
    request_date = Column(Date, default=datetime.date.today)
    priority = Column(String, default="normal") # normal, high, urgent
    status = Column(String, default="pending") # pending, approved, in_progress, completed
    description = Column(Text)
    actual_cost = Column(Float, default=0.0)

    asset = relationship("Asset", back_populates="maintenance_requests")

class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    forecast_date = Column(Date, default=datetime.date.today)
    predicted_qty = Column(Float, default=0.0)
    actual_qty = Column(Float, default=0.0)
    accuracy = Column(Float, default=0.0)
    method = Column(String, default="sma")
    reorder_suggested = Column(Boolean, default=False)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    prediction_date = Column(Date, default=datetime.date.today)
    confidence = Column(Float, default=0.0)
    predicted_failure_date = Column(Date)
    risk_level = Column(String, default="low")
    health_score = Column(Float, default=100.0)
    factors = Column(Text)

    asset = relationship("Asset", back_populates="predictions")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    company_name = Column(String)
    role = Column(String) # Admin, Manager, Technician

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    manager_name = Column(String)
    budget = Column(Float, default=0.0)

class ResourceBooking(Base):
    __tablename__ = "resource_bookings"
    id = Column(Integer, primary_key=True, index=True)
    resource_name = Column(String, index=True)
    booked_by = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String, default="confirmed")

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    auditor_name = Column(String)
    audit_date = Column(Date)
    status = Column(String, default="pending") # pending, passed, failed
    notes = Column(Text)

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String)
    action = Column(String)
    target = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
