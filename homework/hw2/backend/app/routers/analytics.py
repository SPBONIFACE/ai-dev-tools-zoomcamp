from fastapi import APIRouter
from app.models.schemas import AnalyticsSummaryResponse
from app.services.store import store

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary():
    return store.get_analytics_summary()
