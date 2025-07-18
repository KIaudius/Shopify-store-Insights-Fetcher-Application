# Shopify Store Insights Fetcher

A comprehensive Python application that fetches and analyzes Shopify store insights using AI-powered data extraction and competitor analysis.

## Features

### Mandatory Features ✅
- **Product Catalog Extraction**: Fetches complete product listings from `/products.json`
- **Hero Products Detection**: Identifies featured products on homepage
- **Policy Extraction**: Retrieves privacy, return, refund, shipping policies
- **FAQ Extraction**: AI-powered FAQ detection and structuring
- **Contact Information**: Extracts email, phone, address, support hours
- **Social Media Handles**: Identifies Instagram, Facebook, TikTok, etc.
- **Brand Context**: About us, mission, founding details
- **Important Links**: Order tracking, contact us, blogs, etc.

### Bonus Features ✅
- **Competitor Analysis**: AI-powered competitor discovery and analysis
- **MySQL Database**: Persistent storage of all insights
- **Beautiful GUI**: Modern web interface with Bootstrap
- **Deployment Ready**: Configured for Render deployment

## Tech Stack

- **Backend**: FastAPI with Pydantic models
- **AI/ML**: Google Gemini Pro for data structuring
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **Scraping**: BeautifulSoup + Requests
- **Deployment**: Docker + Render

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd "Shopify store Insights-Fetcher Application"

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file based on `.env.example`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=shopify_insights
DEBUG=True
```

**Get Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)

### 3. Database Setup (Optional)

For MySQL persistence (bonus feature):

```bash
# Install MySQL and create database
mysql -u root -p
CREATE DATABASE shopify_insights;
```

### 4. Run the Application

```bash
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit: `http://localhost:8000`

## API Usage

### Scrape Store Insights

```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "website_url": "https://memy.co.in",
    "include_competitor_analysis": true,
    "max_competitors": 3
  }'
```

### Response Format

```json
{
  "success": true,
  "data": {
    "store_url": "https://memy.co.in",
    "store_name": "Memy",
    "brand_context": {
      "brand_description": "...",
      "about_us": "...",
      "mission_statement": "..."
    },
    "product_catalog": [...],
    "hero_products": [...],
    "privacy_policy": {...},
    "faqs": [...],
    "contact_info": {...},
    "social_handles": [...],
    "important_links": [...]
  },
  "competitor_analysis": {
    "competitors": [...],
    "analysis_summary": "...",
    "competitive_advantages": [...],
    "market_insights": [...]
  },
  "processing_time": 15.2
}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web GUI interface |
| GET | `/health` | Health check |
| POST | `/api/scrape` | Main scraping endpoint |
| GET | `/api/insights/{store_url}` | Get stored insights |
| GET | `/api/competitors/{store_url}` | Get competitor analysis |
| GET | `/docs` | API documentation |

## Deployment on Render

### 1. Prepare for Deployment

```bash
# Ensure all files are committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Deploy on Render

1. Visit [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `shopify-insights-fetcher`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables

Add these in Render dashboard:
- `GEMINI_API_KEY`: Your Gemini API key
- `MYSQL_HOST`: Your MySQL host (if using database)
- `MYSQL_PASSWORD`: Your MySQL password
- `DEBUG`: `false`

## Project Structure

```
Shopify store Insights-Fetcher Application/
├── main.py                 # FastAPI application
├── models.py              # Pydantic data models
├── shopify_scraper.py     # Core scraping logic
├── gemini_service.py      # AI/LLM integration
├── database.py            # Database configuration
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── render.yaml           # Render deployment config
├── .env.example          # Environment template
├── templates/
│   └── index.html        # Web GUI
├── static/
│   └── app.js           # Frontend JavaScript
└── README.md            # This file
```

## Key Features Explained

### 1. Shopify Detection
- Validates if URL is a Shopify store
- Checks for Shopify-specific indicators
- Returns 401 error for non-Shopify sites

### 2. AI-Powered Extraction
- Uses Gemini Pro for unstructured data
- Extracts brand context, FAQs, contact info
- Handles different FAQ formats across stores

### 3. Competitor Analysis
- AI discovers competitors automatically
- Scrapes competitor insights
- Provides comparative analysis

### 4. Error Handling
- Comprehensive error responses
- Graceful degradation on failures
- Detailed logging for debugging

## Testing

Test with these sample Shopify stores:
- `https://memy.co.in`
- `https://hairoriginals.com`
- `https://colourpop.com`

## Performance

- Average scraping time: 10-30 seconds
- Concurrent request handling
- Background database operations
- Efficient memory usage

## Security

- Environment variable configuration
- Input validation with Pydantic
- SQL injection prevention
- Rate limiting ready

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review error messages in response
3. Ensure Gemini API key is valid
4. Verify target URL is a Shopify store

---

**Built By Anshuman Mukherjee ❤️ for the GenAI Developer Intern Assignment at DeepSolv**
*This Read.ME is AI Generated*
