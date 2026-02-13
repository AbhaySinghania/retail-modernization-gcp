import os
import psycopg2
from psycopg2.extras import RealDictCursor
from app.models import OrderCreate, make_order


class PostgresOrdersRepo:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),      
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432),
        )
        self._ensure_table()

    def _ensure_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    amount FLOAT NOT NULL,
                    currency TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    idempotency_key TEXT UNIQUE NOT NULL
                );
            """)
            self.conn.commit()

    def create_order(self, order_in: OrderCreate, idempotency_key: str) -> dict:
        order = make_order(order_in, idempotency_key)

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                cur.execute("""
                    INSERT INTO orders (order_id, user_id, amount, currency, status, created_at, idempotency_key)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING *;
                """, (
                    order["order_id"],
                    order["user_id"],
                    order["amount"],
                    order["currency"],
                    order["status"],
                    order["created_at"],
                    order["idempotency_key"],
                ))
                self.conn.commit()
                return cur.fetchone()
            except psycopg2.errors.UniqueViolation:
                self.conn.rollback()
                return self.get_by_idempotency_key(idempotency_key)

    def get_by_idempotency_key(self, idempotency_key: str):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM orders WHERE idempotency_key = %s;", (idempotency_key,))
            return cur.fetchone()

    def list_orders(self, limit: int = 20):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT %s;", (limit,))
            return cur.fetchall()
