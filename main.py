import os
import sys
import warnings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add project root to the Python path to resolve imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now we can import from our app packages
from app.routes.fetch import router as fetch_router
from app.core.database import init_db

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
async def startup_event():
    """Initialize database on startup"""
    print("INFO:     Starting up and initializing database...")
    try:
        init_db()
    except Exception as e:
        print(f"ERROR:    Database initialization failed: {e}")
        print("INFO:     Application will continue without database persistence.")

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
    print("INFO:     Starting server with Uvicorn...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
