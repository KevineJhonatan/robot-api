from fastapi import APIRouter, Depends

from src.modules.webscrapping.views import router as webscraper_router
from src.modules.extract.views import router as extract_router

api_router = APIRouter()

@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "ok"}

api_router.include_router(
    webscraper_router, prefix="/wscrap", tags=["webscrapper"]
)

api_router.include_router(
    extract_router, prefix="/extract", tags=["extract"]
)