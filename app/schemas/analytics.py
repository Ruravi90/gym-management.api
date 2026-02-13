from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class TimeSeriesData(BaseModel):
    date: date
    value: float

class DashboardAnalytics(BaseModel):
    attendance_history: List[TimeSeriesData]
    revenue_history: List[TimeSeriesData]
    membership_distribution: List[dict]  # [{"name": "Monthly", "value": 10}, ...]
    active_clients_count: int
    total_revenue_month: float
    check_ins_today: int

class AnalyticsSummary(BaseModel):
    total_clients: int
    active_memberships: int
    expired_memberships: int
    upcoming_expirations: int
    revenue_month: float
    check_ins_today: int
