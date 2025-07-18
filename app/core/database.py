from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration - use combined URL if available, otherwise build from components
DATABASE_URL = os.getenv("SHOPIFY_INSIGHTS_DB_URL")

if not DATABASE_URL:
    # Fallback to individual parameters
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "shopify_insights")
    DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BrandInsightsDB(Base):
    __tablename__ = "brand_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    store_url = Column(String(500), unique=True, index=True)
    store_name = Column(String(255))
    brand_context = Column(JSON)
    product_catalog = Column(JSON)
    hero_products = Column(JSON)
    total_products = Column(Integer, default=0)
    privacy_policy = Column(JSON)
    return_policy = Column(JSON)
    refund_policy = Column(JSON)
    shipping_policy = Column(JSON)
    terms_of_service = Column(JSON)
    faqs = Column(JSON)
    contact_info = Column(JSON)
    social_handles = Column(JSON)
    important_links = Column(JSON)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    scraping_success = Column(Boolean, default=True)
    errors = Column(JSON)
    
class CompetitorAnalysisDB(Base):
    __tablename__ = "competitor_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    main_brand_url = Column(String(500), index=True)
    competitors = Column(JSON)
    analysis_summary = Column(Text)
    competitive_advantages = Column(JSON)
    market_insights = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    """Create database tables if they don't exist"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        # Test connection by executing a simple query
        with engine.connect() as connection:
            from sqlalchemy import text
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database - test connection first, then create tables if needed"""
    try:
        # First test if we can connect
        if not test_connection():
            print("Cannot connect to database. Check your credentials and database server.")
            return False
        
        print("Database connection successful!")
        
        # Check if tables exist by trying to query one
        try:
            with engine.connect() as connection:
                from sqlalchemy import text
                result = connection.execute(text("SELECT COUNT(*) FROM brand_insights LIMIT 1"))
                print("Database tables already exist and are accessible.")
                return True
        except Exception:
            # Tables don't exist, create them
            print("Creating database tables...")
            if create_tables():
                print("Database tables created successfully!")
                return True
            else:
                print("Failed to create database tables.")
                return False
                
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False
