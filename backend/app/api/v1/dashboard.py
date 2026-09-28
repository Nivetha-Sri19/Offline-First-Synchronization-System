from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_dashboard_service
from app.models.user import User
from app.schemas.sync.response import SyncStatisticsResponse
from app.services.dashboard.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/stats",
    response_model=SyncStatisticsResponse,
)
def dashboard_stats(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> SyncStatisticsResponse:
    return service.get_summary(
        user_id=current_user.id,
    )