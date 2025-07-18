import os
import sys
from sqlalchemy import inspect
from .database import engine, Base, init_db

def check_tables_exist():
    """Check if the required tables exist in the database"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    required_tables = ['brand_insights', 'competitor_analysis']
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        print(f"❌ Missing tables: {', '.join(missing_tables)}")
        return False
    
    print("✅ All required tables exist")
    return True

def main():
    print("🔄 Initializing database...")
    
    # Initialize database
    if not init_db():
        print("❌ Failed to initialize database")
        return 1
    
    # Verify tables were created
    if not check_tables_exist():
        return 1
    
    print("\n✅ Database setup completed successfully!")
    return 0

if __name__ == "__main__":
    # Add project root to the Python path to resolve imports
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from app.core.database import init_db
    sys.exit(main())
