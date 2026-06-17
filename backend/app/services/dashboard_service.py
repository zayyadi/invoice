from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, literal
from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceStatus
from app.models.client import Client
from app.models.payment import Payment


def get_dashboard_metrics(db: Session, user_id: UUID) -> dict:
    """Get comprehensive dashboard metrics for a user."""
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    
    # Invoice counts by status
    invoice_stats = (
        db.query(
            Invoice.status,
            func.count(Invoice.id).label("count"),
            func.sum(Invoice.total_amount).label("total"),
            func.sum(Invoice.paid_amount).label("paid"),
        )
        .filter(Invoice.user_id == user_id)
        .group_by(Invoice.status)
        .all()
    )
    
    status_breakdown = {
        "draft": {"count": 0, "total": 0},
        "sent": {"count": 0, "total": 0},
        "viewed": {"count": 0, "total": 0},
        "partial": {"count": 0, "total": 0},
        "paid": {"count": 0, "total": 0},
        "overdue": {"count": 0, "total": 0},
        "cancelled": {"count": 0, "total": 0},
    }
    
    total_invoiced = 0
    total_paid = 0
    
    for stat in invoice_stats:
        status_key = stat.status.value if hasattr(stat.status, 'value') else stat.status
        status_breakdown[status_key] = {
            "count": stat.count or 0,
            "total": float(stat.total or 0),
            "paid": float(stat.paid or 0),
        }
        total_invoiced += float(stat.total or 0)
        total_paid += float(stat.paid or 0)
    
    # Outstanding amounts
    outstanding = total_invoiced - total_paid
    
    # Overdue invoices
    overdue_invoices = (
        db.query(Invoice)
        .filter(
            Invoice.user_id == user_id,
            Invoice.due_date < today,
            Invoice.status.notin_([InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.DRAFT])
        )
        .order_by(Invoice.due_date.asc())
        .limit(5)
        .all()
    )
    
    overdue_amount = sum(
        float(inv.total_amount) - float(inv.paid_amount) 
        for inv in overdue_invoices
    )
    
    # Recent payments (last 30 days)
    recent_payments = (
        db.query(
            func.count(Payment.id).label("count"),
            func.sum(Payment.amount).label("total"),
        )
        .filter(
            Payment.user_id == user_id,
            Payment.payment_date >= thirty_days_ago
        )
        .first()
    )
    
    # Client statistics
    client_count = (
        db.query(func.count(Client.id))
        .filter(Client.user_id == user_id)
        .scalar()
    )
    
    # Monthly revenue (last 6 months). Keep the grouping in Python so the
    # service works across the app's supported SQLAlchemy test/runtime engines.
    six_months_ago = today - timedelta(days=180)
    recent_payment_rows = (
        db.query(Payment.payment_date, Payment.amount)
        .filter(
            Payment.user_id == user_id,
            Payment.payment_date >= six_months_ago
        )
        .all()
    )
    revenue_by_month: dict[str, float] = {}
    for payment_date, amount in recent_payment_rows:
        month = payment_date.strftime("%Y-%m")
        revenue_by_month[month] = revenue_by_month.get(month, 0) + float(amount or 0)
    
    return {
        "summary": {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "outstanding": outstanding,
            "overdue_amount": overdue_amount,
            "total_invoices": sum(s["count"] for s in status_breakdown.values()),
            "total_clients": client_count,
        },
        "status_breakdown": status_breakdown,
        "recent_activity": {
            "payments_count": recent_payments.count or 0,
            "payments_total": float(recent_payments.total or 0),
        },
        "overdue": {
            "count": len(overdue_invoices),
            "amount": overdue_amount,
            "invoices": [
                {
                    "id": str(inv.id),
                    "invoice_number": inv.invoice_number,
                    "customer_name": inv.customer_name,
                    "due_date": inv.due_date.isoformat(),
                    "amount": float(inv.total_amount) - float(inv.paid_amount),
                    "currency": inv.currency,
                }
                for inv in overdue_invoices
            ],
        },
        "monthly_revenue": [
            {"month": month, "revenue": revenue}
            for month, revenue in sorted(revenue_by_month.items())
        ],
    }


def get_recent_activity(db: Session, user_id: UUID, limit: int = 10) -> list:
    """Get recent activity feed combining invoices and payments."""
    
    # Recent invoices
    recent_invoices = (
        db.query(
            Invoice.id,
            Invoice.invoice_number,
            Invoice.customer_name,
            Invoice.status,
            Invoice.created_at,
            Invoice.total_amount,
            literal("invoice_created").label("activity_type"),
        )
        .filter(Invoice.user_id == user_id)
        .order_by(Invoice.created_at.desc())
        .limit(limit)
        .all()
    )
    
    # Recent payments
    recent_payments = (
        db.query(
            Payment.id,
            Payment.invoice_id,
            Payment.amount,
            Payment.payment_date,
            Invoice.invoice_number,
            Invoice.customer_name,
            literal("payment_received").label("activity_type"),
        )
        .join(Invoice, Payment.invoice_id == Invoice.id)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .limit(limit)
        .all()
    )
    
    # Combine and sort by date
    activities = []
    
    for inv in recent_invoices:
        activities.append({
            "id": str(inv.id),
            "type": "invoice_created",
            "description": f"Invoice {inv.invoice_number} created for {inv.customer_name}",
            "amount": float(inv.total_amount),
            "status": inv.status.value if hasattr(inv.status, 'value') else inv.status,
            "timestamp": inv.created_at.isoformat() if hasattr(inv.created_at, 'isoformat') else str(inv.created_at),
        })
    
    for pay in recent_payments:
        activities.append({
            "id": str(pay.id),
            "type": "payment_received",
            "description": f"Payment received for {pay.invoice_number}",
            "amount": float(pay.amount),
            "invoice_id": str(pay.invoice_id),
            "timestamp": pay.payment_date.isoformat() if hasattr(pay.payment_date, 'isoformat') else str(pay.payment_date),
        })
    
    # Sort by timestamp descending
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return activities[:limit]


def get_upcoming_invoices(db: Session, user_id: UUID, days: int = 7) -> list:
    """Get invoices due in the next N days."""
    today = date.today()
    upcoming_date = today + timedelta(days=days)
    
    invoices = (
        db.query(Invoice)
        .filter(
            Invoice.user_id == user_id,
            Invoice.due_date >= today,
            Invoice.due_date <= upcoming_date,
            Invoice.status.notin_([InvoiceStatus.PAID, InvoiceStatus.CANCELLED]),
        )
        .order_by(Invoice.due_date.asc())
        .limit(5)
        .all()
    )
    
    return [
        {
            "id": str(inv.id),
            "invoice_number": inv.invoice_number,
            "customer_name": inv.customer_name,
            "due_date": inv.due_date.isoformat(),
            "amount": float(inv.total_amount) - float(inv.paid_amount),
            "currency": inv.currency,
            "days_until_due": (inv.due_date - today).days,
        }
        for inv in invoices
    ]
