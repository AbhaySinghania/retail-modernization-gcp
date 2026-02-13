from pydantic import BaseModel
from datetime import datetime, timezone
from uuid import uuid4

class OrderCreate(BaseModel):
    user_id: str
    amount: float
    currency: str = "EUR"

def make_order(order_in: OrderCreate, idempotency_key: str) -> dict:
    return {
        "order_id": str(uuid4()),
        "user_id": order_in.user_id,
        "amount": order_in.amount,
        "currency": order_in.currency,
        "status": "created",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "idempotency_key": idempotency_key,
    }
