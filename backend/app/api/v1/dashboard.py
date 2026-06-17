from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.dashboard_service import (
    get_dashboard_metrics,
    get_recent_activity,
    get_upcoming_invoices,
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/metrics")
def dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard metrics and statistics."""
    return get_dashboard_metrics(db, current_user.id)


@router.get("/activity")
def recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recent activity feed."""
    return get_recent_activity(db, current_user.id, limit)


@router.get("/upcoming")
def upcoming_invoices(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get invoices due in the next N days."""
    return get_upcoming_invoices(db, current_user.id, days)
