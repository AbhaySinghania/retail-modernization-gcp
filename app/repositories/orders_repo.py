from typing import Dict, List, Optional
from app.models import OrderCreate, make_order

class InMemoryOrdersRepo:
    def __init__(self):
        self._orders: List[dict] = []
        self._idem: Dict[str, dict] = {}

    def create_order(self, order_in: OrderCreate, idempotency_key: str) -> dict:
        if idempotency_key in self._idem:
            return self._idem[idempotency_key]

        order = make_order(order_in, idempotency_key)
        self._orders.append(order)
        self._idem[idempotency_key] = order
        return order

    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[dict]:
        return self._idem.get(idempotency_key)

    def list_orders(self, limit: int = 20) -> List[dict]:
        return list(reversed(self._orders))[:limit]
