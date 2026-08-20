from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timedelta, timezone, date
from collections import Counter
from app import crud, models
from app.schemas import analytics as schemas
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.attendance import Attendance
from app.models.membership import Membership, MembershipType
from tortoise.functions import Count, Sum
from tortoise.expressions import Q

router = APIRouter()

@router.get("/dashboard", response_model=schemas.DashboardAnalytics)
async def get_dashboard_analytics(current_user: User = Depends(get_current_user)):
    # Only admin and manager can view analytics
    if current_user.role not in ["admin", "manager", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    today = datetime.now(timezone.utc).date()
    thirty_days_ago = today - timedelta(days=30)
    start_of_today = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
    start_of_thirty_days_ago = datetime.combine(thirty_days_ago, datetime.min.time(), tzinfo=timezone.utc)
    
    # 1. Attendance History (Last 30 days)
    attendances = await Attendance.filter(
        check_in_time__gte=start_of_thirty_days_ago
    ).values("check_in_time")
    
    attendance_counts = Counter()
    for a in attendances:
        d = a["check_in_time"].date()
        attendance_counts[d] += 1
        
    attendance_history = [
        {"date": thirty_days_ago + timedelta(days=i), "value": attendance_counts[thirty_days_ago + timedelta(days=i)]}
        for i in range(31)
    ]

    # 2. Revenue History (Last 30 days)
    memberships = await Membership.filter(
        start_date__gte=start_of_thirty_days_ago
    ).values("start_date", "price_paid")
    
    revenue_sums = Counter()
    for m in memberships:
        d = m["start_date"].date()
        revenue_sums[d] += m["price_paid"] or 0
        
    revenue_history = [
        {"date": thirty_days_ago + timedelta(days=i), "value": float(revenue_sums[thirty_days_ago + timedelta(days=i)])}
        for i in range(31)
    ]

    # 3. Membership Distribution
    dist = await Membership.filter(status="active").values("type")
    type_counts = Counter(d["type"] for d in dist)
    membership_distribution = [{"name": k, "value": v} for k, v in type_counts.items()]

    # 4. General Stats
    active_clients = await models.Client.all().count() # For now total clients as active proxy
    
    # Revenue this month
    first_of_month = today.replace(day=1)
    start_of_month = datetime.combine(first_of_month, datetime.min.time(), tzinfo=timezone.utc)
    month_revenue_data = await Membership.filter(
        start_date__gte=start_of_month
    ).annotate(total=Sum("price_paid")).values("total")
    total_revenue_month = month_revenue_data[0]["total"] if month_revenue_data and month_revenue_data[0]["total"] else 0

    # Check-ins today
    start_of_tomorrow = start_of_today + timedelta(days=1)
    check_ins_today = await Attendance.filter(
        check_in_time__gte=start_of_today,
        check_in_time__lt=start_of_tomorrow
    ).count()

    return {
        "attendance_history": attendance_history,
        "revenue_history": revenue_history,
        "membership_distribution": membership_distribution,
        "active_clients_count": active_clients,
        "total_revenue_month": float(total_revenue_month),
        "check_ins_today": check_ins_today
    }

@router.get("/summary", response_model=schemas.AnalyticsSummary)
async def get_analytics_summary(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "manager", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    today = datetime.now(timezone.utc).date()
    first_of_month = today.replace(day=1)
    start_of_today = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
    start_of_month = datetime.combine(first_of_month, datetime.min.time(), tzinfo=timezone.utc)
    start_of_tomorrow = start_of_today + timedelta(days=1)
    
    total_clients = await models.Client.all().count()
    active_memberships = await Membership.filter(
        status="active",
        end_date__gte=datetime.now(timezone.utc)
    ).count()
    
    expired_memberships = await Membership.filter(
        Q(status="expired") | Q(end_date__lt=datetime.now(timezone.utc))
    ).count()
    
    upcoming_expirations = await Membership.filter(
        status="active",
        end_date__gte=datetime.now(timezone.utc),
        end_date__lte=datetime.now(timezone.utc) + timedelta(days=30)
    ).count()

    revenue_data = await Membership.filter(
        start_date__gte=start_of_month
    ).annotate(total=Sum("price_paid")).values("total")
    revenue_month = revenue_data[0]["total"] if revenue_data and revenue_data[0]["total"] else 0
    
    check_ins_today = await Attendance.filter(
        check_in_time__gte=start_of_today,
        check_in_time__lt=start_of_tomorrow
    ).count()

    return {
        "total_clients": total_clients,
        "active_memberships": active_memberships,
        "expired_memberships": expired_memberships,
        "upcoming_expirations": upcoming_expirations,
        "revenue_month": float(revenue_month),
        "check_ins_today": check_ins_today
    }
