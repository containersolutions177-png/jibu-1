from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import stripe

app = FastAPI(title="Jibu API", version="5.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock")
PAYMENTS_ENABLED = os.getenv("ENVIRONMENT", "demo") == "real"

class CheckoutPayload(BaseModel):
    provider: str
    amount: float
    currency: str = "ZAR"
    item_name: str
    email: str
    return_url: str
    cancel_url: str

# ================= HARDCODED DATA (NO DATABASE CRASHES) =================
USERS = [
    {"id": "u1", "name": "Grace Muthoni", "phone": "+27820001111", "location": "Cape Town", "jibu_score": 85, "wallet_balance": 1500.0}
]

PRODUCTS = [
    {"id": "p1", "name": "Fresh Organic Tomatoes", "description": "1kg farm-fresh", "price": 25.00, "image_url": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400", "stock": 100},
    {"id": "p2", "name": "Handmade Shea Soap", "description": "3 organic soaps", "price": 85.00, "image_url": "https://images.unsplash.com/photo-1607006483225-a6f6b3a4a4a0?w=400", "stock": 45},
    {"id": "p3", "name": "Solar USB Charger", "description": "Portable 20W panel", "price": 199.00, "image_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400", "stock": 20},
    {"id": "p4", "name": "Maize Flour 2kg", "description": "Premium local maize", "price": 35.00, "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400", "stock": 200}
]

ADS = [
    {"id": "a1", "product_id": "p1", "headline": "Morning Freshness", "copy": "Tomatoes picked at sunrise.", "image_url": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400", "impressions": 1520, "clicks": 48, "conversions": 12},
    {"id": "a2", "product_id": "p2", "headline": "Self-Care Made Local", "copy": "Your skin deserves shea butter.", "image_url": "https://images.unsplash.com/photo-1607006483225-a6f6b3a4a4a0?w=400", "impressions": 2300, "clicks": 92, "conversions": 28}
]

# ================= ROUTES =================
@app.get("/")
def root():
    return {"status": "ok", "mode": "real" if PAYMENTS_ENABLED else "demo"}

@app.get("/stats")
def stats():
    ti = sum(a["impressions"] for a in ADS)
    tc = sum(a["clicks"] for a in ADS)
    tcv = sum(a["conversions"] for a in ADS)
    return {
        "users": {"total": len(USERS)},
        "commerce": {"products": len(PRODUCTS)},
        "safiri": {
            "ads": len(ADS), "impressions": ti, "clicks": tc, "conversions": tcv,
            "click_rate": round(tc / max(ti, 1) * 100, 2),
            "conversion_rate": round(tcv / max(tc, 1) * 100, 2),
            "bounce_rate": round((1 - tc / max(ti, 1)) * 100, 2),
        }
    }

@app.get("/users/{user_id}")
def get_user(user_id: str):
    for u in USERS:
        if u["id"] == user_id: return u
    raise HTTPException(404, "User not found")

@app.get("/products")
def get_products():
    return PRODUCTS

@app.get("/ads")
def get_ads():
    return ADS

@app.post("/module/{name}")
def test_module(name: str):
    msgs = {
        "mentor": "AI Tutor: Your algebra score improved by 15%. Local tutor assigned.",
        "duka": "Duka POS: Inventory scanned. 3 items low. Restock order sent to Soko.",
        "tiba": "Tiba Health: Symptoms indicate flu. Local nurse will call in 10 mins.",
        "soko": "Soko Market: Matched with 3 local buyers. Delivery rider assigned.",
        "sheria": "Sheria Legal: Rental contract generated. Paralegal reviewing it now.",
        "kazi": "Kazi Gigs: Matched with local plumbing job (R150). Route optimized.",
        "pesa": "Pesa Savings: Chama group created. Wallet balance updated.",
        "mtaa": "Mtaa Alerts: Local alert - Heavy traffic on N1 due to accident."
    }
    return {"status": "success", "message": msgs.get(name, "AI Module tested successfully.")}

@app.post("/checkout")
async def checkout(req: CheckoutPayload, x_jibu_mode: Optional[str] = Header(None)):
    if x_jibu_mode != "real" or not PAYMENTS_ENABLED:
        return {"payment_url": "DEMO_BYPASS", "message": "Demo mode: Payment bypassed."}

    if req.provider.lower() == "stripe":
        try:
            stripe.api_key = STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price_data": {"currency": req.currency.lower(), "product_data": {"name": req.item_name}, "unit_amount": int(req.amount * 100)}, "quantity": 1}],
                mode="payment", success_url=req.return_url, cancel_url=req.cancel_url
            )
            return {"payment_url": session.url}
        except Exception as e:
            raise HTTPException(500, f"Stripe Error: {str(e)}")
    
    return {"payment_url": f"https://sandbox.payfast.co.za/eng/process?amount={req.amount}"}
