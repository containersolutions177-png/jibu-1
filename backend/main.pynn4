from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os
import hashlib
import urllib.parse
import stripe

app = FastAPI(title="Jibu API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ENVIRONMENT VARIABLES =================
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")

# ================= MODELS =================
class CheckoutPayload(BaseModel):
    provider: str
    amount: float
    currency: str = "ZAR"
    item_name: str
    email: str
    return_url: str
    cancel_url: str
    notify_url: str

# ================= DATA =================
USERS = [
    {"id": "u1", "name": "Grace Muthoni", "phone": "+27820001111", "location": "Cape Town", "jibu_score": 85, "wallet_balance": 1500.00},
    {"id": "u2", "name": "James Ochieng", "phone": "+27820002222", "location": "Joburg", "jibu_score": 92, "wallet_balance": 450.50},
]

PRODUCTS = [
    {"id": "p1", "name": "Fresh Organic Tomatoes", "description": "1kg farm-fresh", "price": 25.00, "currency": "ZAR", "image_url": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400", "stock": 100},
    {"id": "p2", "name": "Handmade Shea Soap Set", "description": "3 organic soaps", "price": 85.00, "currency": "ZAR", "image_url": "https://images.unsplash.com/photo-1607006483225-a6f6b3a4a4a0?w=400", "stock": 45},
    {"id": "p3", "name": "Solar USB Charger", "description": "Portable 20W panel", "price": 199.00, "currency": "ZAR", "image_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400", "stock": 20},
]

ADS = [
    {"id": "a1", "product_id": "p1", "headline": "Morning Freshness", "copy": "Tomatoes picked at sunrise.", "image_url": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400", "impressions": 1520, "clicks": 48, "conversions": 12},
    {"id": "a2", "product_id": "p2", "headline": "Self-Care Made Local", "copy": "Your skin deserves shea butter.", "image_url": "https://images.unsplash.com/photo-1607006483225-a6f6b3a4a4a0?w=400", "impressions": 2300, "clicks": 92, "conversions": 28},
]

# ================= ROUTES =================
@app.get("/")
def root():
    return {"status": "ok", "service": "Jibu API"}

@app.get("/stats")
def stats():
    ti = sum(a["impressions"] for a in ADS)
    tc = sum(a["clicks"] for a in ADS)
    tcv = sum(a["conversions"] for a in ADS)
    return {
        "users": {"total": len(USERS)},
        "commerce": {"products": len(PRODUCTS), "revenue": 0},
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
        if u["id"] == user_id:
            return u
    return {"error": "User not found"}

@app.get("/products")
def get_products(): return PRODUCTS

@app.get("/ads")
def get_ads(): return ADS

# Mock Module Endpoints
@app.post("/module/{name}")
def test_module(name: str):
    if name == "mentor": return {"status": "success", "message": "AI assessed your math level. Local tutor assigned."}
    if name == "duka": return {"status": "success", "message": "Inventory scanned. 3 items low on stock."}
    if name == "tiba": return {"status": "success", "message": "Symptoms analyzed. Nurse will call in 10 mins."}
    if name == "soko": return {"status": "success", "message": "Matched with 3 local buyers."}
    if name == "sheria": return {"status": "success", "message": "Rental contract generated. Paralegal reviewing."}
    if name == "kazi": return {"status": "success", "message": "Gig matched: Plumbing help (R150)."}
    if name == "pesa": return {"status": "success", "message": "Chama group created. Savings tracked."}
    if name == "mtaa": return {"status": "success", "message": "Local alert: Traffic on N1."}
    return {"status": "error", "message": "Unknown module"}

@app.post("/checkout")
async def checkout(req: CheckoutPayload):
    provider = req.provider.lower()
    
    if provider == "payfast":
        base = "https://sandbox.payfast.co.za/eng/process"
        return {"payment_url": f"{base}?amount={req.amount}&item_name={req.item_name}"}
    elif provider == "ozow":
        return {"payment_url": f"https://pay.ozow.com/?amount={req.amount}"}
    elif provider == "stripe":
        stripe.api_key = STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price_data": {"currency": req.currency.lower(), "product_data": {"name": req.item_name}, "unit_amount": int(req.amount * 100)}, "quantity": 1}],
                mode="payment", success_url=req.return_url, cancel_url=req.cancel_url
            )
            return {"payment_url": session.url}
        except:
            return {"payment_url": "https://checkout.stripe.com/pay/cs_test_mock"}
    return {"payment_url": "https://example.com/mock-payment"}
