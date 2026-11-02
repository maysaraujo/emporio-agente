import pandas as pd
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent
DB_PATH = DATA_DIR / "store.db"

# CSV filename
TABLES = [
  "categories",
  "customers",
  "products",
  "orders",
  "order_items",
  "promotions"
]

def load():
  conn = sqlite3.connect(DB_PATH)
  for table in TABLES:
    csv_path = DATA_DIR / f"{table}.csv"
    df = pd.read_csv(csv_path)
    df.to_sql(table, conn, if_exists="replace", index=False)
    print(f" {table}: {len(df)} rows")
  conn.close()
  print(f"\nDatabase created at {DB_PATH}")

if __name__ == "__main__":
  load()
