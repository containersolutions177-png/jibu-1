from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings
import os

# Use Postgres in Real mode, In-Memory SQLite in Demo mode for serverless reliability
if settings.ENVIRONMENT == "real" and settings.DATABASE_URL:
    db_url = settings.DATABASE_URL
    connect_args = {}
else:
    db_url = "sqlite:///:memory:"
    connect_args = {"check_same_thread": False}

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    location = Column(String)
    jibu_score = Column(Integer, default=100)
    wallet_balance = Column(Float, default=0.0)
    is_admin = Column(Boolean, default=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    image_url = Column(String)
    stock = Column(Integer)

class Ad(Base):
    __tablename__ = "ads"
    id = Column(String, primary_key=True, index=True)
    product_id = Column(String)
    headline = Column(String)
    copy = Column(String)
    image_url = Column(String)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
