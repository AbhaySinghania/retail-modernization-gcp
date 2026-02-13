from fastapi import FastAPI, Header, HTTPException
from typing import Optional

from app.models import OrderCreate
from app.repositories.orders_repo import InMemoryOrdersRepo

app = FastAPI()

from app.config import get_repo_type

repo_type = get_repo_type()

if repo_type == "postgres":
    # Only works when DB env vars exist
    from app.repositories.postgres_orders_repo import PostgresOrdersRepo
    repo = PostgresOrdersRepo()
else:
    repo = InMemoryOrdersRepo()


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/orders")
def create_order(
    payload: OrderCreate,
    idempotency_key: Optional[str] = Header(default=None, convert_underscores=False, alias="Idempotency-Key"),
):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key header")

    existing = repo.get_by_idempotency_key(idempotency_key)
    if existing:
        return {"result": "duplicate_request_returned_existing", "order": existing}

    order = repo.create_order(payload, idempotency_key)
    return {"result": "created", "order": order}

@app.get("/orders")
def list_orders(limit: int = 20):
    orders = repo.list_orders(limit=limit)
    return {"count": len(orders), "orders": orders}
