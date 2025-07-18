from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import time

from ..core.models import ScrapingRequest, ScrapingResponse, BrandInsights, CompetitorAnalysis
from ..services.shopify_scraper import ShopifyScraper
from ..services.gemini_service import GeminiService
from ..core.database import get_db, BrandInsightsDB, CompetitorAnalysisDB

router = APIRouter()

# Initialize services
scraper = ShopifyScraper()
gemini_service = GeminiService()

@router.post("/scrape", response_model=ScrapingResponse)
async def scrape_store(
    request: ScrapingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    start_time = time.time()
    
    try:
        store_url = str(request.website_url)
        
        if not store_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        brand_insights = scraper.scrape_store(store_url)
        
        if not brand_insights.scraping_success:
            if "not appear to be a Shopify store" in str(brand_insights.errors):
                raise HTTPException(status_code=401, detail="Website not found or not a Shopify store")
            else:
                raise HTTPException(status_code=500, detail=f"Scraping failed: {'; '.join(brand_insights.errors)}")
        
        background_tasks.add_task(save_brand_insights, brand_insights, db)
        
        response_data = {
            "success": True,
            "data": brand_insights,
            "message": "Store insights scraped successfully",
            "processing_time": round(time.time() - start_time, 2),
            "errors": brand_insights.errors
        }
        
        if request.include_competitor_analysis:
            try:
                competitor_analysis = await analyze_competitors(
                    brand_insights, 
                    request.max_competitors,
                    background_tasks,
                    db
                )
                response_data["competitor_analysis"] = competitor_analysis
            except Exception as e:
                response_data["errors"].append(f"Competitor analysis failed: {e}")

        return ScrapingResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

async def analyze_competitors(
    main_brand: BrandInsights, 
    max_competitors: int,
    background_tasks: BackgroundTasks,
    db: Session
):
    competitor_urls = gemini_service.find_competitors(main_brand.store_name)
    
    competitors_data = []
    for url in competitor_urls[:max_competitors]:
        try:
            competitor_insights = scraper.scrape_store(url)
            if competitor_insights.scraping_success:
                competitors_data.append(competitor_insights)
        except Exception as e:
            print(f"Error scraping competitor {url}: {e}")

    if not competitors_data:
        return None

    analysis_results = gemini_service.analyze_competitors(
        main_brand.dict(), 
        [c.dict() for c in competitors_data]
    )
    
    competitor_analysis = CompetitorAnalysis(
        main_brand=main_brand,
        competitors=competitors_data,
        **analysis_results
    )
    
    background_tasks.add_task(save_competitor_analysis, competitor_analysis, db)
    
    return competitor_analysis

def save_brand_insights(brand_insights: BrandInsights, db: Session):
    try:
        db_insights = db.query(BrandInsightsDB).filter(
            BrandInsightsDB.store_url == brand_insights.store_url
        ).first()
        
        if db_insights:
            # Update existing record
            for key, value in brand_insights.dict().items():
                setattr(db_insights, key, value)
        else:
            # Create new record
            db_insights = BrandInsightsDB(**brand_insights.dict())
            db.add(db_insights)
        
        db.commit()
        print(f"Saved brand insights for {brand_insights.store_url}")
        
    except Exception as e:
        db.rollback()
        print(f"Error saving brand insights: {e}")

def save_competitor_analysis(analysis: CompetitorAnalysis, db: Session):
    try:
        db_analysis = CompetitorAnalysisDB(
            main_brand_url=analysis.main_brand.store_url,
            competitors=[comp.dict() for comp in analysis.competitors],
            analysis_summary=analysis.analysis_summary,
            competitive_advantages=analysis.competitive_advantages,
            market_insights=analysis.market_insights
        )
        
        db.add(db_analysis)
        db.commit()
        print(f"Saved competitor analysis for {analysis.main_brand.store_url}")
        
    except Exception as e:
        db.rollback()
        print(f"Error saving competitor analysis: {e}")

@router.get("/insights/{store_url:path}")
async def get_stored_insights(store_url: str, db: Session = Depends(get_db)):
    try:
        insights = db.query(BrandInsightsDB).filter(
            BrandInsightsDB.store_url == store_url
        ).first()
        
        if not insights:
            raise HTTPException(status_code=404, detail="Store insights not found")
        
        return {
            "success": True,
            "data": insights,
            "message": "Stored insights retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving insights: {str(e)}")

@router.get("/competitors/{store_url:path}")
async def get_competitor_analysis(store_url: str, db: Session = Depends(get_db)):
    try:
        analysis = db.query(CompetitorAnalysisDB).filter(
            CompetitorAnalysisDB.main_brand_url == store_url
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Competitor analysis not found")
        
        return {
            "success": True,
            "data": analysis,
            "message": "Competitor analysis retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving competitor analysis: {str(e)}")
