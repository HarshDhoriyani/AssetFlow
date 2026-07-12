from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Base schemas
class AssetBase(BaseModel):
    name: str
    asset_code: str
    category: str
    state: str = "active"
    purchase_value: float = 0.0
    current_location: str
    assigned_to: str
    health_score: float = 100.0
    risk_level: str = "low"
    image_url: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    class Config:
        from_attributes = True

class MaintenanceRequestBase(BaseModel):
    name: str
    asset_id: int
    requested_by: str
    assigned_to: str
    request_date: date
    priority: str = "normal"
    status: str = "pending"
    description: str
    actual_cost: float = 0.0

class MaintenanceRequestCreate(MaintenanceRequestBase):
    pass

class MaintenanceRequest(MaintenanceRequestBase):
    id: int
    class Config:
        from_attributes = True

class DemandForecastBase(BaseModel):
    product_name: str
    forecast_date: date
    predicted_qty: float
    actual_qty: float
    accuracy: float
    method: str
    reorder_suggested: bool

class DemandForecastCreate(DemandForecastBase):
    pass

class DemandForecast(DemandForecastBase):
    id: int
    class Config:
        from_attributes = True

class PredictionBase(BaseModel):
    asset_id: int
    prediction_date: date
    confidence: float
    predicted_failure_date: date
    risk_level: str
    health_score: float
    factors: str

class PredictionCreate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    company_name: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    company_name: str
    role: str
    
    class Config:
        from_attributes = True

class Department(BaseModel):
    id: int
    name: str
    manager_name: str
    budget: float
    class Config: from_attributes = True

class ResourceBooking(BaseModel):
    id: int
    resource_name: str
    booked_by: str
    start_time: str
    end_time: str
    status: str
    class Config: from_attributes = True

class Audit(BaseModel):
    id: int
    title: str
    auditor_name: str
    audit_date: date
    status: str
    notes: str
    class Config: from_attributes = True

class ActivityLog(BaseModel):
    id: int
    user_email: str
    action: str
    target: str
    timestamp: str
    class Config: from_attributes = True
