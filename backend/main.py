from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

app = FastAPI(title="Jibu API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ MODELS ============
class User(BaseModel):
    id: str
    name: str
    phone: str
    location: str
    jibu_score: int = 100
    wallet_balance: float = 0.0

class Order(BaseModel):
    user_id: str
    product_id: str
    amount: float

class ContractReq(BaseModel):
    type: str
    parties: List[str]
    terms: dict

class ChamaReq(BaseModel):
    name: str
    members: List[str]
    contribution: float

# ============ MOCK DATA ============
USERS = [
    {"id": "u1", "name": "Grace Muthoni", "phone": "+254700111111", "location": "Nairobi", "jibu_score": 85, "wallet_balance": 150.00},
    {"id": "u2", "name": "James Ochieng", "phone": "+254700222222", "location": "Kisumu", "jibu_score": 92, "wallet_balance": 45.50},
    {"id": "u3", "name": "Fatima Hassan", "phone": "+254700333333", "location": "Mombasa", "jibu_score": 60, "wallet_balance": 12.00},
]

PRODUCTS = [
    {"id": "p1", "name": "Fresh Organic Tomatoes", "description": "1kg farm-fresh from Kiambu", "price": 1.50, "currency": "USD", "seller_id": "s1", "category": "groceries", "image_url": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400&h=400&fit=crop", "stock": 100},
    {"id": "p2", "name": "Handmade Shea Soap Set", "description": "3 organic soaps, local shea butter", "price": 5.00, "currency": "USD", "seller_id": "s2", "category": "wellness", "image_url": "https://images.unsplash.com/photo-1607006483225-a6f6b3a4a4a0?w=400&h=400&fit=crop", "stock": 45},
    {"id": "p3", "name": "Solar USB Charger", "description": "Portable 20W solar panel", "price": 12.00, "currency": "USD", "seller_id": "s3", "category": "electronics", "image_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400&h=400&fit=crop", "stock": 20},
    {"id": "p4", "name": "Fortified Maize Flour 2kg", "description": "Quality ugali flour", "price": 2.20, "currency": "USD", "seller_id": "s1", "category": "groceries", "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=400&fit=crop", "stock": 200},
    {"id": "p5", "name": "Swahili Storybook Set", "description": "5 books for early readers", "price": 8.50, "currency": "USD", "seller_id": "s4", "category": "education", "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=400&fit=crop", "stock": 30},
    {"id": "p6", "name": "Bamboo Toothbrush 4-Pack", "description": "Eco-friendly, biodegradable", "price": 3.00, "currency": "USD", "seller_id": "s2", "category": "wellness", "image_url": "https://images.unsplash.com/photo-1607613009820-a29f7bb81c04?w=400&h=400&fit=crop", "stock": 80},
]

ADS = [
    {"id": "a1", "product_id": "p1", "headline": "Morning Freshness", "copy": "Tomatoes picked at sunrise. Delivered by lunch.", "image_url": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400&h=400&fit=crop", "target_audience": "families", "time_slot": "6-9am", "weather_trigger": "sunny", "impressions": 1520, "clicks": 48, "conversions": 12},
    {"id": "a2", "product_id": "p2", "headline": "Self-Care Made Local", "copy": "Your skin deserves shea butter from the village.", "image_url": "https://images.unsplash.com/photo-1607006483225-a6f6b3a4a4a0?w=400&h=400&fit=crop", "target_audience": "women", "time_slot": "8-11pm", "weather_trigger": None, "impressions": 2300, "clicks": 92, "conversions": 28},
    {"id": "a3", "product_id": "p3", "headline": "Never Run Out of Power", "copy": "Solar charger for when the grid fails.", "image_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400&h=400&fit=crop", "target_audience": "students", "time_slot": "10am-2pm", "weather_trigger": "cloudy", "impressions": 890, "clicks": 35, "conversions": 8},
    {"id": "a4", "product_id": "p6", "headline": "Small Change, Big Impact", "copy": "Switch to bamboo. 4 brushes, zero plastic.", "image_url": "https://images.unsplash.com/photo-1607613009820-a29f7bb81c04?w=400&h=400&fit=crop", "target_audience": "eco-conscious", "time_slot": "all", "weather_trigger": None, "impressions": 1100, "clicks": 41, "conversions": 15},
]

ORDERS: List[dict] = []

# ============ HEALTH ============
@app.get("/")
def root():
    return {"status": "ok", "service": "Jibu API", "modules": 9, "version": "1.0.0"}

# ============ STATS ============
@app.get("/stats")
def stats():
    ti = sum(a["impressions"] for a in ADS)
    tc = sum(a["clicks"] for a in ADS)
    tcv = sum(a["conversions"] for a in ADS)
    return {
        "modules": ["Mentor", "Duka", "Tiba", "Soko", "Sheria", "Kazi", "Pesa", "Mtaa", "Safiri"],
        "users": {"total": len(USERS), "avg_score": round(sum(u["jibu_score"] for u in USERS) / max(len(USERS), 1), 1)},
        "commerce": {"products": len(PRODUCTS), "orders": len(ORDERS), "revenue": round(sum(o["amount"] for o in ORDERS if o["status"] == "completed"), 2)},
        "safiri": {
            "ads": len(ADS),
            "impressions": ti,
            "clicks": tc,
            "conversions": tcv,
            "click_rate": round(tc / max(ti, 1) * 100, 2),
            "conversion_rate": round(tcv / max(tc, 1) * 100, 2),
            "bounce_rate": round((1 - tc / max(ti, 1)) * 100, 2),
        },
    }

# ============ USERS ============
@app.get("/users")
def get_users():
    return USERS

@app.get("/users/{user_id}")
def get_user(user_id: str):
    for u in USERS:
        if u["id"] == user_id:
            return u
    raise HTTPException(404, "User not found")

# ============ PRODUCTS ============
@app.get("/products")
def get_products(category: Optional[str] = None):
    if category:
        return [p for p in PRODUCTS if p["category"] == category]
    return PRODUCTS

@app.get("/products/{product_id}")
def get_product(product_id: str):
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    raise HTTPException(404, "Product not found")

# ============ SAFIRI ============
@app.get("/ads")
def get_ads(time: Optional[str] = None, weather: Optional[str] = None):
    results = list(ADS)
    if time:
        results = [a for a in results if a["time_slot"] == time or a["time_slot"] == "all"]
    if weather and weather != "none":
        results = [a for a in results if a["weather_trigger"] == weather or a["weather_trigger"] is None]
    results.sort(key=lambda a: a["conversions"] / max(a["impressions"], 1), reverse=True)
    return results

@app.post("/ads/{ad_id}/click")
def click_ad(ad_id: str):
    for a in ADS:
        if a["id"] == ad_id:
            a["clicks"] += 1
            for p in PRODUCTS:
                if p["id"] == a["product_id"]:
                    return {"ad": a, "product": p}
    raise HTTPException(404, "Ad not found")

# ============ ORDERS ============
@app.post("/orders")
def create_order(o: Order):
    user = next((u for u in USERS if u["id"] == o.user_id), None)
    if not user:
        raise HTTPException(404, "User not found")
    order = {"id": str(uuid.uuid4()), "user_id": o.user_id, "product_id": o.product_id, "amount": o.amount, "created_at": datetime.utcnow().isoformat()}
    if user["wallet_balance"] >= o.amount:
        user["wallet_balance"] -= o.amount
        order["status"] = "completed"
        for a in ADS:
            if a["product_id"] == o.product_id:
                a["conversions"] += 1
    else:
        order["status"] = "failed_insufficient"
    ORDERS.append(order)
    return order

@app.get("/orders/{user_id}")
def get_orders(user_id: str):
    return [o for o in ORDERS if o["user_id"] == user_id]

# ============ MODULE 1: MENTOR ============
@app.post("/mentor/assess")
def mentor_assess(user_id: str):
    score = 68
    return {"user_id": user_id, "score": score, "level": "intermediate", "recommendation": "Focus on algebra fundamentals", "tutor_assigned": True}

# ============ MODULE 2: DUKA ============
@app.post("/duka/scan")
def duka_scan():
    return {"detected": ["Tomatoes", "Onions", "Maize Flour"], "low_stock": ["Cooking Oil"], "predicted_stockout_days": 5}

# ============ MODULE 3: TIBA ============
@app.post("/tiba/symptoms")
def tiba_symptoms(symptoms: List[str]):
    severity = "low"
    if "fever" in symptoms and "cough" in symptoms:
        severity = "medium"
    if "chest pain" in symptoms or "bleeding" in symptoms:
        severity = "high"
    return {"symptoms": symptoms, "severity": severity, "advice": "Rest and hydrate" if severity == "low" else "Consult a nurse within 2 hours", "nurse_assigned": severity != "low"}

# ============ MODULE 4: SOKO ============
@app.post("/soko/match")
def soko_match():
    return {"matches": [{"name": "Sarah's Kitchen", "distance": "3km", "needs": 50}, {"name": "City Fresh Market", "distance": "8km", "needs": 200}], "total_demand": 250}

# ============ MODULE 5: SHERIA ============
@app.post("/sheria/contract")
def sheria_contract(c: ContractReq):
    body = f"CONTRACT OF {c.type.upper()}\n\nParties: {', '.join(c.parties)}\nDate: {datetime.utcnow().strftime('%Y-%m-%d')}\n\nTerms:\n"
    for k, v in c.terms.items():
        body += f"- {k}: {v}\n"
    body += "\nAI-generated. Pending paralegal review."
    return {"contract": body, "paralegal_assigned": True}

# ============ MODULE 6: KAZI ============
@app.get("/kazi/gigs/{user_id}")
def kazi_gigs(user_id: str):
    return {"gigs": [{"title": "Plumbing Help", "pay": 15.00, "distance": "3km", "rating": 4.5}, {"title": "House Cleaning", "pay": 10.00, "distance": "5km", "rating": 4.2}, {"title": "Math Tutoring", "pay": 12.00, "distance": "2km", "rating": 4.8}]}

# ============ MODULE 7: PESA ============
@app.post("/pesa/chama")
def pesa_chama(c: ChamaReq):
    return {"chama_id": str(uuid.uuid4()), "name": c.name, "members": c.members, "total_pot": c.contribution * len(c.members), "loan_recommendation": round(c.contribution * 3, 2)}

# ============ MODULE 8: MTAA ============
@app.get("/mtaa/alerts/{location}")
def mtaa_alerts(location: str):
    return {"location": location, "alerts": [
        {"type": "road", "message": "Heavy traffic on Thika Road", "time": "2 min ago"},
        {"type": "weather", "message": "Light rain expected in 1 hour", "time": "15 min ago"},
        {"type": "security", "message": "Police patrol increased in Westlands", "time": "45 min ago"},
    ]}
