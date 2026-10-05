"""
schemas/analytics.py — dashboard analytics shape (mirrors CLAUDE.md §Analytics APIs).
"""
from pydantic import BaseModel


class DashboardData(BaseModel):
    """The headline numbers shown on the analytics dashboard."""

    total_requests: int
    active_requests: int
    avg_response_time_min: float
    completion_rate: float
    by_service_type: dict[str, int]   # {"RESCUE": 180, "MEDICAL": 450, ...}
    by_status: dict[str, int]         # {"SUBMITTED": 34, "APPROVED": 11, ...}


class DashboardResponse(BaseModel):
    """Envelope for GET /analytics/dashboard ({status, data})."""

    status: str = "success"
    data: DashboardData
