from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any

from .database.database import engine, get_db
from .models import url as models
from .schemas.url import URLCreate, URLResponse
from .services.url_service import URLService

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="""
    A modern URL shortening service API built with FastAPI.
    
    ## Features
    * Shorten long URLs
    * Custom short code generation
    * Click tracking
    * URL statistics
    * Redis caching for improved performance
    
    ## Technologies
    * FastAPI
    * PostgreSQL
    * Redis Cache
    * Docker
    """,
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    """Custom OpenAPI schema"""
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

@app.post("/shorten", 
    response_model=URLResponse,
    summary="Create a shortened URL",
    description="""
    Creates a shortened URL from a long URL.
    
    - Validates the input URL
    - Checks for existing shortened URLs
    - Generates a unique short code
    - Returns both original and shortened URLs
    - Caches the result for faster access
    """,
    response_description="The shortened URL object"
)
def create_short_url(
    url_create: URLCreate, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """Create a shortened URL from a long URL"""
    url_service = URLService(db)
    try:
        result = url_service.create_short_url(
            str(url_create.url), 
            str(request.base_url)
        )
        return URLResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/{short_code}",
    response_class=RedirectResponse,
    summary="Redirect to original URL",
    description="""
    Redirects to the original URL using the short code.
    
    - Checks cache for quick lookup
    - Falls back to database if not in cache
    - Increments the click counter
    - Redirects to the original URL
    """,
    responses={
        307: {"description": "Temporary redirect to the original URL"},
        404: {"description": "URL not found"}
    }
)
def redirect_to_url(
    short_code: str, 
    db: Session = Depends(get_db)
):
    """Redirect to the original URL"""
    url_service = URLService(db)
    original_url = url_service.get_original_url(short_code)
    
    if not original_url:
        raise HTTPException(
            status_code=404, 
            detail="Short URL not found"
        )
    
    return RedirectResponse(url=original_url)

@app.get("/url/{short_code}/stats",
    response_model=Dict[str, Any],
    summary="Get URL statistics",
    description="""
    Retrieves statistics for a shortened URL.
    
    Returns:
    - Original URL
    - Short code
    - Number of clicks
    - Creation timestamp
    
    Statistics are cached for improved performance.
    """,
    responses={
        200: {
            "description": "URL statistics",
            "content": {
                "application/json": {
                    "example": {
                        "original_url": "https://example.com",
                        "short_code": "abc123",
                        "clicks": 42,
                        "created_at": "2024-01-16T12:00:00"
                    }
                }
            }
        },
        404: {"description": "URL not found"}
    }
)
def get_url_stats(
    short_code: str, 
    db: Session = Depends(get_db)
):
    """Get statistics for a shortened URL"""
    url_service = URLService(db)
    stats = url_service.get_url_stats(short_code)
    
    if not stats:
        raise HTTPException(
            status_code=404, 
            detail="URL not found"
        )
    
    return stats
