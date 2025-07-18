from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Product(BaseModel):
    id: Optional[int] = None
    title: str
    handle: str
    description: Optional[str] = None
    price: Optional[str] = None
    compare_at_price: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: List[str] = []
    images: List[str] = []
    variants: List[Dict[str, Any]] = []
    available: bool = True
    url: Optional[str] = None

class FAQ(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None

class SocialHandle(BaseModel):
    platform: str
    url: str
    handle: Optional[str] = None

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    support_hours: Optional[str] = None

class Policy(BaseModel):
    title: str
    content: str
    url: Optional[str] = None
    last_updated: Optional[str] = None

class ImportantLink(BaseModel):
    title: str
    url: str
    description: Optional[str] = None

class BrandContext(BaseModel):
    store_url: str
    store_name: Optional[str] = None
    brand_description: Optional[str] = None
    about_us: Optional[str] = None
    mission_statement: Optional[str] = None
    founded_year: Optional[str] = None
    headquarters: Optional[str] = None

class BrandInsights(BaseModel):
    # Basic Info
    store_url: str
    store_name: Optional[str] = None
    brand_context: Optional[BrandContext] = None
    
    # Products
    product_catalog: List[Product] = []
    hero_products: List[Product] = []
    total_products: int = 0
    
    # Policies
    privacy_policy: Optional[Policy] = None
    return_policy: Optional[Policy] = None
    refund_policy: Optional[Policy] = None
    shipping_policy: Optional[Policy] = None
    terms_of_service: Optional[Policy] = None
    
    # Customer Support
    faqs: List[FAQ] = []
    contact_info: Optional[ContactInfo] = None
    
    # Social & Links
    social_handles: List[SocialHandle] = []
    important_links: List[ImportantLink] = []
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.now)
    scraping_success: bool = True
    errors: List[str] = []

class CompetitorAnalysis(BaseModel):
    main_brand: BrandInsights
    competitors: List[BrandInsights] = []
    analysis_summary: Optional[str] = None
    competitive_advantages: List[str] = []
    market_insights: List[str] = []

class ScrapingRequest(BaseModel):
    website_url: HttpUrl
    include_competitor_analysis: bool = False
    max_competitors: int = Field(default=3, ge=1, le=10)

class ScrapingResponse(BaseModel):
    success: bool
    data: Optional[BrandInsights] = None
    competitor_analysis: Optional[CompetitorAnalysis] = None
    message: str
    processing_time: Optional[float] = None
    errors: List[str] = []
