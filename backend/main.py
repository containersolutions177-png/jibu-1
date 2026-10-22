from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import uuid
import os

from database import engine, Base, get_db, User, Product, Ad

# Create tables in memory
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jibu API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
PAYMENTS_ENABLED = os.getenv("PAYMENTS_ENABLED", "false").lower() == "true"

# ================= SCHEMAS =================
class CheckoutPayload(BaseModel):
    provider: str
    amount: float
    currency: str = "ZAR"
    item_name: str
    email: str
    return_url: str
    cancel_url: str
    notify_url: str

# ================= SEED DATA (Run on startup) =================
@app.on_event("startup")
def seed_db():
    db = next(get_db())
    if not db.query(User).first():
        db.add(User(id="u1", name="Grace Muthoni", phone="+27820001111", location="Cape Town", jibu_score=85, wallet_balance=1500.0, is_admin=True))
        db.add(User(id="u2", name="James Ochieng", phone="+27820002222", location="Joburg", jibu_score=92, wallet_balance=450.0))
        
        db.add(Product(id="p1", name="Fresh Organic Tomatoes", description="1kg farm-fresh", price=25.00, image_url="https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400", stock=100))
        db.add(Product(id="p2", name="Handmade Shea Soap", description="3 organic soaps", price=85.00, image_url="https://images.unsplash.com/photo-1607006483225-a6f6b3a4a4a0?w=400", stock=45))
        db.add(Product(id="p3", name="Solar USB Charger", description="Portable 20W panel", price=199.00, image_url="https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400", stock=20))
        
        db.add(Ad(id="a1", product_id="p1", headline="Morning Freshness", copy="Tomatoes picked at sunrise.", image_url="https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400", impressions=1520, clicks=48, conversions=12))
        db.add(Ad(id="a2", product_id="p2", headline="Self-Care Made Local", copy="Your skin deserves shea butter.", image_url="https://images.unsplash.com/photo-1607006483225-a6f6b3a4a4a0?w=400", impressions=2300, clicks=92, conversions=28))
        db.commit()

# ================= ROUTES =================
@app.get("/")
def root():
    return {"status": "ok", "service": "Jibu Core API", "db_connected": True}

@app.get("/config")
def get_config():
    return {"payments_enabled": PAYMENTS_ENABLED}

@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    ads = db.query(Ad).all()
    ti = sum(a.impressions for a in ads)
    tc = sum(a.clicks for a in ads)
    tcv = sum(a.conversions for a in ads)
    users = db.query(User).count()
    
    return {
        "users": {"total": users},
        "commerce": {"products": db.query(Product).count()},
        "safiri": {
            "ads": len(ads), "impressions": ti, "clicks": tc, "conversions": tcv,
            "click_rate": round(tc / max(ti, 1) * 100, 2),
            "conversion_rate": round(tcv / max(tc, 1) * 100, 2),
            "bounce_rate": round((1 - tc / max(ti, 1)) * 100, 2),
        }
    }

@app.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    return {"id": user.id, "name": user.name, "jibu_score": user.jibu_score}

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/ads")
def get_ads(db: Session = Depends(get_db)):
    return db.query(Ad).all()

@app.post("/module/{name}")
def test_module(name: str):
    msgs = {
        "mentor": "AI assessed your math level. Local tutor assigned.",
        "duka": "Inventory scanned. 3 items low on stock.",
        "tiba": "Symptoms analyzed. Nurse will call in 10 mins.",
        "soko": "Matched with 3 local buyers.",
        "sheria": "Rental contract generated. Paralegal reviewing.",
        "kazi": "Gig matched: Plumbing help (R150).",
        "pesa": "Chama group created. Savings tracked.",
        "mtaa": "Local alert: Traffic on N1."
    }
    return {"status": "success", "message": msgs.get(name, "Module tested.")}

@app.post("/checkout")
async def checkout(req: CheckoutPayload):
    if not PAYMENTS_ENABLED:
        return {"payment_url": "TEST_MODE_BYPASS", "message": "Payments disabled. Demo mode active."}
    
    # Real Gateway Routing (Plugs into your sandbox credentials)
    if req.provider == "payfast":
        return {"payment_url": f"https://sandbox.payfast.co.za/eng/process?amount={req.amount}&item_name={req.item_name}"}
    elif req.provider == "ozow":
        return {"payment_url": f"https://pay.ozow.com/?amount={req.amount}"}
    elif req.provider == "stripe":
        return {"payment_url": "https://checkout.stripe.com/pay/cs_test_mock"}
    
    return {"payment_url": "https://example.com/mock-payment"}
