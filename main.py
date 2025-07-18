import os
import sys
import warnings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log
import logging

# Add project root to the Python path to resolve imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now we can import from our app packages
from app.routes.fetch import router as fetch_router
from app.core.database import init_db

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Suppress Pydantic UserWarning for field name shadowing
warnings.filterwarnings(
    "ignore",
    message=r'Field name ".+" shadows an attribute in parent "Operation";',
    category=UserWarning,
    module=r"pydantic\._internal\._fields"
)

app = FastAPI(
    title="Shopify Store Insights Fetcher",
    description="A comprehensive API to fetch and analyze Shopify store insights",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
@retry(
    wait=wait_fixed(5),
    stop=stop_after_attempt(6),
    before_sleep=before_sleep_log(logger, logging.INFO),
)
async def startup_event():
    """
    Initialize the database connection on startup with retry logic.
    """
    try:
        logger.info("Attempting to connect to the database...")
        init_db()
        logger.info("Database connection successful.")
    except Exception as e:
        logger.error(f"Database connection failed after multiple retries: {e}")
        logger.warning("Application will continue without database persistence.")

# Include API router
app.include_router(fetch_router, prefix="/api")

# Mount static files for the GUI
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main GUI page from templates/index.html"""
    try:
        with open("templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>API is running. Frontend not found.</h1><p>Visit /docs for API documentation.</p>")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify that the server is running."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server with Uvicorn on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
