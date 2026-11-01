# Query tools the agent can call. Each returns plain Python data
# (lists/dicts) that the agent turns into a natural-language reply.

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "store.db"

def _connect():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row # rows behave like dicts
  return conn

def search_products(query=None, category=None, max_price=None, min_price=None):
  sql = """
  SELECT p.name, p.price_brl, p.stock_quantity, p.status,
         c.name AS category
  FROM products p
  JOIN categories c ON c.category_id = p.category_id
  WHERE 1 = 1
         """
  params = []

  if query:
    sql += " AND p.name LIKE ?"
    params.append(f"%{query}%")
  if category:
    sql += " AND c.name LIKE ?"
    params.append(f"%{category}%")
  if max_price is not None:
    sql += " AND p.price_brl <= ?"
    params.append(max_price)
  if min_price is not None:
    sql += " AND p.price_brl >= ?"
    params.append(min_price)
  sql += " ORDER BY p.price_brl ASC LIMIT 20"

  conn = _connect()
  rows = conn.execute(sql, params).fetchall()
  conn.close()
  return [dict(r) for r in rows]

def get_order_status(tracking_code):
  conn = _connect()
  order = conn.execute(
    """
    SELECT order_id, order_date, status, total_brl,
           payment_method, tracking_code, estimated_delivery
    FROM orders
    WHERE tracking_code = ?
    """,
    [tracking_code],
  ).fetchone()
  conn.close()
  if order is None:
    return None
  return dict(order)

def check_promotion(product_name):
  conn = _connect()
  rows = conn.execute(
    """
    SELECT p.name AS product, pr.description, pr.discount_percent,
           p.price_brl
    FROM promotions pr
    JOIN products p ON p.product_id = pr.product_id
    WHERE pr.is_active = 1 AND p.name LIKE ?
    """,
    [f"%{product_name}%"],
  ).fetchall()
  conn.close()
  return [dict(r) for r in rows]

# Schemas: how the model "sees" each tool (OpenAI/Groq function-calling format)
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Busca instrumentos no catálogo da loja. Use para perguntas "
                "sobre disponibilidade, preço ou modelos. Retorna nome, preço, "
                "estoque, status e categoria."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Trecho do nome do produto, ex: 'Takamine'",
                    },
                    "category": {
                        "type": "string",
                        "description": "Categoria, ex: 'Violões', 'Guitarras', 'Teclados e Pianos'",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Preço máximo em reais",
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Preço mínimo em reais",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": (
                "Consulta o status de um pedido pelo código de rastreio. "
                "Peça o código ao cliente; nunca busque pedido por nome."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tracking_code": {
                        "type": "string",
                        "description": "Código de rastreio, formato BR + 9 caracteres + BR",
                    },
                },
                "required": ["tracking_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_promotion",
            "description": (
                "Verifica se um produto tem promoção ATIVA. Retorna lista vazia "
                "se não houver. Use antes de mencionar qualquer desconto."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Trecho do nome do produto",
                    },
                },
                "required": ["product_name"],
            },
        },
    },
]

# Maps a tool name to its function, so the loop can dispatch calls
TOOL_FUNCTIONS = {
    "search_products": search_products,
    "get_order_status": get_order_status,
    "check_promotion": check_promotion,
}
