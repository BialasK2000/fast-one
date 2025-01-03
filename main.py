from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
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


@app.post("/orders/", response_model=OrderResponse)
def create_order(order: OrderCreate):
    db: Session = SessionLocal()
    new_order = Order(
        customer_name=order.customer_name,
        total_amount=order.total_amount,
        currency=order.currency
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    db.close()
    return fetch_converted_order(new_order)


@app.put("/orders/{order_id}/", response_model=OrderResponse)
def update_order(order_id: int, update_data: OrderUpdate):
    db: Session = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        db.close()
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = update_data.status
    db.commit()
    db.refresh(order)
    db.close()
    return fetch_converted_order(order)


@app.get("/orders/{order_id}/", response_model=OrderResponse)
def get_order(order_id: int):
    db: Session = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        db.close()
        raise HTTPException(status_code=404, detail="Order not found")

    response = fetch_converted_order(order)
    db.close()
    return response


@app.get("/orders/", response_model=List[OrderResponse])
def list_orders(status: Optional[OrderStatus] = Query(None)):
    db: Session = SessionLocal()
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    orders = query.all()
    db.close()
    return [fetch_converted_order(order) for order in orders]


def fetch_converted_order(order: Order) -> OrderResponse:
    converted_amount = None
    if order.currency.upper() != "PLN":
        try:
            response = requests.get(f"https://api.nbp.pl/api/exchangerates/rates/a/{order.currency}/?format=json")
            response.raise_for_status()
            rate = response.json()["rates"][0]["mid"]
            converted_amount = order.total_amount / rate
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Currency conversion failed: {str(e)}")

    return OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        total_amount=order.total_amount,
        converted_amount=converted_amount,
        currency=order.currency,
        status=order.status
    )
