from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import datetime

import models, schemas, auth
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AssetFlow API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Seed Database
import random

@app.on_event("startup")
def seed_db():
    db = SessionLocal()
    if db.query(models.Asset).count() == 0:
        categories = ["Lab Equipment", "Facilities", "IT Hardware", "Vehicles", "Heavy Machinery"]
        locations = ["Lab A", "Lab B", "Roof East", "Server Room 1", "Warehouse", "Field Site"]
        users = ["Dr. Smith", "Maintenance Dept", "John Doe", "Jane Roe", "Alice", "Bob"]
        
        # 1. Generate Departments
        deps = []
        for d in ["Engineering", "Research", "Maintenance", "IT Support", "Operations"]:
            dep = models.Department(name=d, manager_name=random.choice(users), budget=random.randint(50000, 500000))
            db.add(dep)
            deps.append(dep)
        
        # 2. Generate 50 Assets
        assets = []
        for i in range(1, 51):
            category = random.choice(categories)
            state = random.choices(["active", "maintenance", "allocated", "retired"], weights=[0.6, 0.2, 0.15, 0.05])[0]
            asset = models.Asset(
                name=f"{category} Model {i*10}",
                asset_code=f"AST-{i:03d}",
                category=category,
                state=state,
                purchase_value=round(random.uniform(1000, 50000), 2),
                current_location=random.choice(locations),
                assigned_to=random.choice(users),
                health_score=round(random.uniform(20.0, 100.0) if state != "active" else random.uniform(70.0, 100.0), 1),
                risk_level="low" if state == "active" else random.choice(["medium", "high", "critical"]),
                image_url=f"https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=500&q=80" if category != "IT Hardware" else "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500&q=80"
            )
            db.add(asset)
            assets.append(asset)
        db.commit()

        # 3. Generate Predictions & Maintenance for some assets
        for asset in assets:
            if asset.risk_level in ["high", "critical"] or asset.health_score < 50:
                pred = models.Prediction(
                    asset_id=asset.id,
                    prediction_date=datetime.date.today(),
                    confidence=round(random.uniform(0.7, 0.99), 2),
                    predicted_failure_date=datetime.date.today() + datetime.timedelta(days=random.randint(1, 14)),
                    risk_level=asset.risk_level,
                    health_score=asset.health_score,
                    factors=random.choice(["High vibration detected.", "Motor temperature anomaly.", "Unusual power draw.", "Component fatigue expected."])
                )
                db.add(pred)

                req = models.MaintenanceRequest(
                    name=f"MR-2026-{asset.id:03d}",
                    asset_id=asset.id,
                    requested_by="AI System",
                    assigned_to=random.choice(users),
                    request_date=datetime.date.today(),
                    priority="high" if asset.risk_level == "critical" else "normal",
                    status="pending",
                    description=f"Auto-generated predictive maintenance trigger.",
                    actual_cost=round(random.uniform(100, 1500), 2)
                )
                db.add(req)

        # 4. Generate Bookings, Audits, ActivityLogs
        for _ in range(10):
            db.add(models.ResourceBooking(
                resource_name=f"Meeting Room {random.choice(['A', 'B', 'C'])}",
                booked_by=random.choice(users),
                start_time=datetime.datetime.now() + datetime.timedelta(days=random.randint(1,5)),
                end_time=datetime.datetime.now() + datetime.timedelta(days=random.randint(1,5), hours=2)
            ))
            db.add(models.Audit(
                title=f"Q{random.randint(1,4)} Safety Audit",
                auditor_name=random.choice(users),
                audit_date=datetime.date.today() - datetime.timedelta(days=random.randint(1,30)),
                status=random.choice(["passed", "failed", "pending"]),
                notes="Standard compliance check."
            ))
            db.add(models.ActivityLog(
                user_email="system@assetflow.com",
                action="ASSET_CREATED",
                target=random.choice(assets).asset_code
            ))
            
        # 5. Generate Demand Forecasts
        for _ in range(8):
            db.add(models.DemandForecast(
                product_name=random.choice(["HVAC Filter Pack", "Motor Bearings", "Lubricant Oil 5L", "Coolant 10L", "Replacement Drive Belt", "Sensors Pack"]),
                forecast_date=datetime.date.today(),
                predicted_qty=round(random.uniform(20.0, 150.0), 1),
                actual_qty=round(random.uniform(15.0, 160.0), 1),
                accuracy=round(random.uniform(85.0, 99.0), 1),
                method=random.choice(["sma", "ewma"]),
                reorder_suggested=random.choice([True, False])
            ))
            
        db.commit()
    db.close()

# --- AUTH ROUTES ---

@app.post("/api/auth/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        company_name=user.company_name,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# --- DATA ROUTES (PROTECTED) ---

@app.get("/api/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    total_assets = db.query(models.Asset).count()
    active_assets = db.query(models.Asset).filter(models.Asset.state == "active").count()
    maintenance_reqs = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.status == "pending").count()
    high_risk_assets = db.query(models.Prediction).filter(models.Prediction.risk_level.in_(["high", "critical"])).count()

    return {
        "total_assets": total_assets,
        "active_assets": active_assets,
        "pending_maintenance": maintenance_reqs,
        "high_risk_assets": high_risk_assets
    }

@app.get("/api/assets", response_model=List[schemas.Asset])
def get_assets(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Asset).all()

@app.get("/api/predictions", response_model=List[schemas.Prediction])
def get_predictions(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Prediction).all()

@app.get("/api/maintenance", response_model=List[schemas.MaintenanceRequest])
def get_maintenance_requests(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.MaintenanceRequest).all()

@app.get("/api/forecasts", response_model=List[schemas.DemandForecast])
def get_forecasts(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.DemandForecast).all()

@app.get("/api/departments", response_model=List[schemas.Department])
def get_departments(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Department).all()

@app.get("/api/bookings", response_model=List[schemas.ResourceBooking])
def get_bookings(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.ResourceBooking).all()

@app.get("/api/audits", response_model=List[schemas.Audit])
def get_audits(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Audit).all()

@app.get("/api/activity", response_model=List[schemas.ActivityLog])
def get_activity_logs(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.ActivityLog).order_by(models.ActivityLog.timestamp.desc()).all()

# --- ADMIN RBAC ENDPOINTS ---

@app.get("/api/users", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    return db.query(models.User).all()

@app.post("/api/assets", response_model=schemas.Asset)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    db_asset = models.Asset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

@app.put("/api/assets/{asset_id}", response_model=schemas.Asset)
def update_asset(asset_id: int, asset: schemas.AssetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    for key, value in asset.model_dump().items():
        setattr(db_asset, key, value)
    db.commit()
    db.refresh(db_asset)
    return db_asset

@app.post("/api/departments", response_model=schemas.Department)
def create_department(dept: schemas.DepartmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    db_dept = models.Department(**dept.model_dump())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@app.put("/api/departments/{dept_id}", response_model=schemas.Department)
def update_department(dept_id: int, dept: schemas.DepartmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
    for key, value in dept.model_dump().items():
        setattr(db_dept, key, value)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@app.post("/api/bookings", response_model=schemas.ResourceBooking)
def create_booking(booking: schemas.ResourceBookingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    from dateutil import parser
    start_dt = parser.parse(booking.start_time)
    end_dt = parser.parse(booking.end_time)
    
    # Overlap logic
    overlapping = db.query(models.ResourceBooking).filter(
        models.ResourceBooking.resource_name == booking.resource_name,
        models.ResourceBooking.status == "confirmed",
        models.ResourceBooking.start_time < end_dt,
        models.ResourceBooking.end_time > start_dt
    ).first()
    
    if overlapping:
        raise HTTPException(status_code=400, detail="Resource is already booked during this time.")
        
    db_booking = models.ResourceBooking(
        resource_name=booking.resource_name,
        booked_by=booking.booked_by,
        start_time=start_dt,
        end_time=end_dt,
        status="confirmed"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking
