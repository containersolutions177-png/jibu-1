from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid
import stripe
from typing import Optional

from config import settings
from database import engine, Base, get_db, User, Product, Ad

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jibu API", version="4.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutPayload(BaseModel):
    provider: str
    amount: float
    currency: str = "ZAR"
    item_name: str
    email: str
    return_url: str
    cancel_url: str

@app.on_event("startup")
def seed_db():
    # Seed data if in demo mode
    if settings.ENVIRONMENT == "demo":
        db = next(get_db())
        try:
            if not db.query(User).first():
                db.add(User(id="u1", name="Grace Muthoni", phone="+27820001111", location="Cape Town", jibu_score=85, wallet_balance=1500.0, is_admin=True))
                db.add(Product(id="p1", name="Fresh Organic Tomatoes", description="1kg farm-fresh", price=25.00, image_url="https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400", stock=100))
                db.add(Product(id="p2", name="Handmade Shea Soap", description="3 organic soaps", price=85.00, image_url="https://images.unsplash.com/photo-1607006483225-a6f6b3a4a4a0?w=400", stock=45))
                db.add(Ad(id="a1", product_id="p1", headline="Morning Freshness", copy="Tomatoes picked at sunrise.", image_url="https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400", impressions=1520, clicks=48, conversions=12))
                db.commit()
        except Exception as e:
            print(f"Seed error: {e}")
        finally:
            db.close()

@app.get("/")
def root():
    return {"status": "ok", "mode": settings.ENVIRONMENT}

@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    try:
        ads = db.query(Ad).all()
        ti = sum(a.impressions for a in ads)
        tc = sum(a.clicks for a in ads)
        tcv = sum(a.conversions for a in ads)
        return {
            "users": {"total": db.query(User).count()},
            "commerce": {"products": db.query(Product).count()},
            "safiri": {
                "ads": len(ads), "impressions": ti, "clicks": tc, "conversions": tcv,
                "click_rate": round(tc / max(ti, 1) * 100, 2),
                "conversion_rate": round(tcv / max(tc, 1) * 100, 2),
                "bounce_rate": round((1 - tc / max(ti, 1)) * 100, 2),
            }
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user: raise HTTPException(404, "User not found")
        return {"id": user.id, "name": user.name, "jibu_score": user.jibu_score}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/ads")
def get_ads(db: Session = Depends(get_db)):
    return db.query(Ad).all()

@app.post("/checkout")
async def checkout(req: CheckoutPayload, x_jibu_mode: Optional[str] = Header(None)):
    if x_jibu_mode != "real" or settings.ENVIRONMENT != "real":
        return {"payment_url": "DEMO_BYPASS", "message": "Demo mode: Payment bypassed."}

    provider = req.provider.lower()
    if provider == "stripe":
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price_data": {"currency": req.currency.lower(), "product_data": {"name": req.item_name}, "unit_amount": int(req.amount * 100)}, "quantity": 1}],
                mode="payment", success_url=req.return_url, cancel_url=req.cancel_url
            )
            return {"payment_url": session.url}
        except Exception as e:
            raise HTTPException(500, str(e))
    
    return {"payment_url": "https://example.com/mock-payment"}
