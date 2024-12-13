from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from enum import Enum as PyEnum

app = FastAPI()

DATABASE_URL = "sqlite:///./orders.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class OrderStatus(PyEnum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)


Base.metadata.create_all(bind=engine)


class OrderCreate(BaseModel):
    customer_name: str = Field(..., example="John Doe")
    total_amount: float = Field(..., gt=0, example=100.0)
    currency: str = Field(..., example="EUR")


class OrderUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    total_amount: float
    converted_amount: Optional[float] = None
    currency: str
    status: OrderStatus
