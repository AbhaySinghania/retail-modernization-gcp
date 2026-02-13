from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import uuid4
from datetime import datetime, timezone

app = FastAPI()

# In-memory store for now (DB comes later)
ORDERS: List[dict] = []
IDEMPOTENCY_MAP: Dict[str, dict] = {}

class OrderCreate(BaseModel):
    user_id: str
    amount: float
    currency: str = "EUR"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/orders")
def create_order(
    payload: OrderCreate,
    idempotency_key: Optional[str] = Header(default=None, convert_underscores=False, alias="Idempotency-Key"),
):
    # Idempotency is required for reliability story
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key header")

    # If request is retried with same key, return the same order
    if idempotency_key in IDEMPOTENCY_MAP:
        return {"result": "duplicate_request_returned_existing", "order": IDEMPOTENCY_MAP[idempotency_key]}

    order = {
        "order_id": str(uuid4()),
        "user_id": payload.user_id,
        "amount": payload.amount,
        "currency": payload.currency,
        "status": "created",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "idempotency_key": idempotency_key,
    }
    ORDERS.append(order)
    IDEMPOTENCY_MAP[idempotency_key] = order

    return {"result": "created", "order": order}

@app.get("/orders")
def list_orders(limit: int = 20):
    # newest first
    return {"count": min(limit, len(ORDERS)), "orders": list(reversed(ORDERS))[:limit]}
