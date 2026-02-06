from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.membership import Membership
from ..schemas.membership import MembershipCreate, MembershipUpdate
from datetime import datetime, timedelta

def get_membership(db: Session, membership_id: int):
    """Get a specific membership by ID"""
    return db.query(Membership).filter(Membership.id == membership_id).first()

def get_memberships_by_client(db: Session, client_id: int):
    """Get all memberships for a specific client"""
    return db.query(Membership).filter(Membership.client_id == client_id).all()

def get_active_membership(db: Session, client_id: int):
    """Get the currently active membership for a client"""
    return (
        db.query(Membership)
        .filter(
            and_(
                Membership.client_id == client_id,
                Membership.status == "active",
                Membership.end_date >= datetime.utcnow()
            )
        )
        .order_by(Membership.end_date.desc())
        .first()
    )

def get_memberships(db: Session, skip: int = 0, limit: int = 100):
    """Get all memberships with pagination"""
    return db.query(Membership).offset(skip).limit(limit).all()

def create_membership(db: Session, membership: MembershipCreate):
    """Create a new membership"""
    db_membership = Membership(**membership.dict())
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

def update_membership(db: Session, membership_id: int, membership_update: MembershipUpdate):
    """Update a membership"""
    db_membership = get_membership(db, membership_id)
    if db_membership:
        update_data = membership_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_membership, field, value)
        db.commit()
        db.refresh(db_membership)
    return db_membership

def delete_membership(db: Session, membership_id: int):
    """Delete a membership"""
    db_membership = get_membership(db, membership_id)
    if db_membership:
        db.delete(db_membership)
        db.commit()
    return db_membership

def get_expired_memberships(db: Session):
    """Get all expired memberships"""
    return (
        db.query(Membership)
        .filter(
            or_(
                Membership.end_date < datetime.utcnow(),
                Membership.status == "expired"
            )
        )
        .all()
    )

def get_memberships_by_status(db: Session, status: str):
    """Get all memberships with a specific status"""
    return db.query(Membership).filter(Membership.status == status).all()

def get_memberships_by_payment_status(db: Session, payment_status: str):
    """Get all memberships with a specific payment status"""
    return db.query(Membership).filter(Membership.payment_status == payment_status).all()

def get_total_memberships_count(db: Session):
    """Get the total count of all memberships"""
    return db.query(Membership).count()

def get_active_memberships_count(db: Session):
    """Get the count of active memberships"""
    return (
        db.query(Membership)
        .filter(
            and_(
                Membership.status == "active",
                Membership.end_date >= datetime.utcnow()
            )
        )
        .count()
    )

def get_expired_memberships_count(db: Session):
    """Get the count of expired memberships"""
    return (
        db.query(Membership)
        .filter(
            or_(
                Membership.end_date < datetime.utcnow(),
                Membership.status == "expired"
            )
        )
        .count()
    )

def get_upcoming_expirations(db: Session, days: int = 30):
    """Get memberships that will expire within the specified number of days"""
    future_date = datetime.utcnow() + timedelta(days=days)
    return (
        db.query(Membership)
        .filter(
            and_(
                Membership.status == "active",
                Membership.end_date >= datetime.utcnow(),
                Membership.end_date <= future_date
            )
        )
        .order_by(Membership.end_date.asc())
        .all()
    )
