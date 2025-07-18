import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("SHOPIFY_INSIGHTS_DB_URL")
print(f"Connecting to: {DB_URL.split('@')[-1]}")  # Don't print full URL with credentials

try:
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        tables = conn.execute(text("SHOW TABLES"))
        print("Existing tables:", [t[0] for t in tables.fetchall()])
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")