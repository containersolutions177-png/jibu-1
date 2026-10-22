from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
import hashlib
import urllib.parse
import httpx
import stripe
from datetime import datetime

app = FastAPI(title="Jibu API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ENVIRONMENT VARIABLES =================
# (Vercel will inject these if you set them in the dashboard, otherwise defaults are used)
PAYFAST_MERCHANT_ID = os.getenv("PAYFAST_MERCHANT_ID", "10000100")
PAYFAST_MERCHANT_KEY = os.getenv("PAYFAST_MERCHANT_KEY", "46f0cd694581a")
PAYFAST_PASSPHRASE = os.getenv("PAYFAST_PASSPHRASE", "jt7NOE43FZPn")

OZOW_SITE_CODE = os.getenv("OZOW_SITE_CODE", "TSTSTE0001")
OZOW_PRIVATE_KEY = os.getenv("OZOW_PRIVATE_KEY", "215114531AFF7134A94C88DE3EB50F5754D08C3E7B8C04F3A9F791E83C7D8809")
OZOW_API_KEY = os.getenv("OZOW_API_KEY", "")

PEACH_CLIENT_ID = os.getenv("PEACH_CLIENT_ID", "")
PEACH_CLIENT_SECRET = os.getenv("PEACH_CLIENT_SECRET", "")
PEACH_MERCHANT_ID = os.getenv("PEACH_MERCHANT_ID", "")

STITCH_CLIENT_ID = os.getenv("STITCH_CLIENT_ID", "")
STITCH_CLIENT_SECRET = os.getenv("STITCH_CLIENT_SECRET", "")
STITCH_ACCOUNT = os.getenv("STITCH_ACCOUNT", "62000000000")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")

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

class OrderReq(BaseModel):
    user_id: str
    product_id: str
    amount: float

# ================= MOCK DATA =================
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

ORDERS = []

# ================= CORE ROUTES =================
@app.get("/")
def root():
    return {"status": "ok", "service": "Jibu API", "version": "2.0.0"}

@app.get("/stats")
def stats():
    ti = sum(a["impressions"] for a in ADS)
    tc = sum(a["clicks"] for a in ADS)
    tcv = sum(a["conversions"] for a in ADS)
    return {
        "modules": ["Mentor", "Duka", "Tiba", "Soko", "Sheria", "Kazi", "Pesa", "Mtaa", "Safiri"],
        "users": {"total": len(USERS)},
        "commerce": {"products": len(PRODUCTS), "orders": len(ORDERS), "revenue": sum(o["amount"] for o in ORDERS if o["status"] == "completed")},
        "safiri": {
            "ads": len(ADS), "impressions": ti, "clicks": tc, "conversions": tcv,
            "click_rate": round(tc / max(ti, 1) * 100, 2),
            "conversion_rate": round(tcv / max(tc, 1) * 100, 2),
            "bounce_rate": round((1 - tc / max(ti, 1)) * 100, 2),
        }
    }

@app.get("/products")
def get_products(): return PRODUCTS

@app.get("/ads")
def get_ads(): return ADS

@app.post("/orders")
def create_order(o: OrderReq):
    user = next((u for u in USERS if u["id"] == o.user_id), None)
    if not user: raise HTTPException(404, "User not found")
    order = {"id": str(uuid.uuid4()), "user_id": o.user_id, "product_id": o.product_id, "amount": o.amount, "status": "pending"}
    user["wallet_balance"] -= o.amount
    order["status"] = "completed"
    ORDERS.append(order)
    return order

# ================= PAYMENT ENGINE =================
@app.post("/checkout")
async def checkout(req: CheckoutPayload):
    provider = req.provider.lower()
    
    if provider == "payfast":
        base = "https://sandbox.payfast.co.za/eng/process"
        data = {
            "merchant_id": PAYFAST_MERCHANT_ID, "merchant_key": PAYFAST_MERCHANT_KEY,
            "return_url": req.return_url, "cancel_url": req.cancel_url, "notify_url": req.notify_url,
            "email_address": req.email, "m_payment_id": req.item_name.replace(" ", "_"),
            "amount": f"{req.amount:.2f}", "item_name": req.item_name
        }
        param_string = urllib.parse.urlencode(data)
        if PAYFAST_PASSPHRASE: param_string += f"&passphrase={PAYFAST_PASSPHRASE}"
        data["signature"] = hashlib.md5(param_string.encode()).hexdigest()
        return {"provider": "payfast", "payment_url": f"{base}?{urllib.parse.urlencode(data)}"}

    elif provider == "ozow":
        base = "https://pay.ozow.com/"
        data = {
            "SiteCode": OZOW_SITE_CODE, "CountryCode": "ZA", "CurrencyCode": req.currency,
            "Amount": f"{req.amount:.2f}", "TransactionReference": req.item_name.replace(" ", "_"),
            "BankReference": "Jibu", "Customer": req.email, "NotifyUrl": req.notify_url,
            "SuccessUrl": req.return_url, "CancelUrl": req.cancel_url, "IsTest": "true"
        }
        hash_str = "".join(str(v) for k, v in sorted(data.items())) + OZOW_PRIVATE_KEY
        data["HashCheck"] = hashlib.sha512(hash_str.encode()).hexdigest()
        return {"provider": "ozow", "payment_url": f"{base}?{urllib.parse.urlencode(data)}"}

    elif provider == "stripe":
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": req.currency.lower(), "product_data": {"name": req.item_name}, "unit_amount": int(req.amount * 100)}, "quantity": 1}],
            mode="payment", success_url=req.return_url, cancel_url=req.cancel_url, customer_email=req.email
        )
        return {"provider": "stripe", "payment_url": session.url}

    elif provider == "paypal":
        base = "https://api-m.sandbox.paypal.com"
        auth_str = hashlib.sha256()
        # Simplified PayPal Logic for MVP (Assumes valid credentials)
        return {"provider": "paypal", "payment_url": "https://www.sandbox.paypal.com/checkoutnow?token=MOCK_TOKEN"}

    elif provider == "stitch":
        # Stitch Pay by Bank
        return {"provider": "stitch", "payment_url": "https://secure.stitch.money/connect/authorize?client_id=MOCK&redirect_uri=MOCK"}

    elif provider == "peach":
        return {"provider": "peach", "payment_url": "https://sandbox.peachpayments.com/checkout/MOCK"}

    raise HTTPException(400, "Invalid payment provider")
