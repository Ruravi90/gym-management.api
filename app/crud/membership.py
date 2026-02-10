from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.membership import Membership, MembershipType
from ..schemas.membership import MembershipCreate, MembershipUpdate, MembershipTypeCreate, MembershipTypeUpdate
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


# CRUD operations for MembershipType
def get_membership_type(db: Session, membership_type_id: int):
    """Get a specific membership type by ID"""
    return db.query(MembershipType).filter(MembershipType.id == membership_type_id).first()

def get_membership_types(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False):
    """Get all membership types with optional filtering"""
    query = db.query(MembershipType)
    if active_only:
        query = query.filter(MembershipType.is_active == True)
    return query.offset(skip).limit(limit).all()

def create_membership_type(db: Session, membership_type: MembershipTypeCreate):
    """Create a new membership type"""
    db_membership_type = MembershipType(**membership_type.dict())
    db.add(db_membership_type)
    db.commit()
    db.refresh(db_membership_type)
    return db_membership_type

def update_membership_type(db: Session, membership_type_id: int, membership_type_update: MembershipTypeUpdate):
    """Update a membership type"""
    db_membership_type = get_membership_type(db, membership_type_id)
    if db_membership_type:
        update_data = membership_type_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_membership_type, field, value)
        db.commit()
        db.refresh(db_membership_type)
    return db_membership_type

def delete_membership_type(db: Session, membership_type_id: int):
    """Deactivate a membership type (soft delete)"""
    db_membership_type = get_membership_type(db, membership_type_id)
    if db_membership_type:
        db_membership_type.is_active = False
        db.commit()
        db.refresh(db_membership_type)
    return db_membership_type


# Enhanced CRUD operations for Membership with new features
def create_membership(db: Session, membership: MembershipCreate):
    """Create a new membership with automatic date calculation based on membership type"""
    # If membership_type_id is provided, get the type to calculate dates
    membership_type = None
    if membership.membership_type_id:
        membership_type = get_membership_type(db, membership.membership_type_id)
    
    # Calculate end_date if not provided and membership type exists
    start_date = membership.start_date or datetime.utcnow()
    end_date = membership.end_date
    
    if membership_type and not end_date:
        if membership_type.duration_days:
            end_date = start_date + timedelta(days=membership_type.duration_days)
        else:
            # Default to 30 days if no duration specified
            end_date = start_date + timedelta(days=30)
    
    # Set price_paid to membership_type.price if not provided
    price_paid = membership.price_paid or (membership_type.price if membership_type else membership.price)
    
    db_membership = Membership(
        client_id=membership.client_id,
        membership_type_id=membership.membership_type_id,
        type=membership.type or (membership_type.name if membership_type else "General"),
        start_date=start_date,
        end_date=end_date,
        price=membership_type.price if membership_type else membership.price,
        price_paid=price_paid,
        status=membership.status,
        payment_status=membership.payment_status,
        payment_method=membership.payment_method,
        notes=membership.notes
    )
    
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

def increment_access_count(db: Session, membership_id: int):
    """Increment the access counter for punch-based memberships"""
    db_membership = get_membership(db, membership_id)
    if db_membership:
        db_membership.accesses_used += 1
        db.commit()
        db.refresh(db_membership)
    return db_membership

def get_punch_usage(db: Session, membership_id: int):
    """Get access usage statistics for a membership"""
    membership = get_membership(db, membership_id)
    if not membership or not membership.membership_type:
        return None
        
    total_accesses = membership.membership_type.accesses_allowed
    accesses_used = membership.accesses_used
    accesses_remaining = None if total_accesses is None else max(0, total_accesses - accesses_used)
    
    return {
        "total_accesses_allowed": total_accesses,
        "accesses_used": accesses_used,
        "accesses_remaining": accesses_remaining
    }

def validate_membership_access(db: Session, client_id: int):
    """Validate if a client has valid access rights"""
    # Get the currently active membership for the client
    active_membership = get_active_membership(db, client_id)
    
    if not active_membership:
        return {
            "valid_access": False,
            "message": "No active membership found"
        }
    
    # Check if it's a punch-based membership and if accesses are available
    if active_membership.membership_type and active_membership.membership_type.accesses_allowed is not None:
        if active_membership.accesses_used >= active_membership.membership_type.accesses_allowed:
            return {
                "valid_access": False,
                "message": "Access limit exceeded for punch-based membership"
            }
    
    # Check if the membership hasn't expired
    if active_membership.end_date < datetime.utcnow():
        return {
            "valid_access": False,
            "message": "Membership has expired"
        }
    
    # Access is valid
    total_accesses = active_membership.membership_type.accesses_allowed if active_membership.membership_type else None
    accesses_remaining = None if total_accesses is None else max(0, total_accesses - active_membership.accesses_used) if active_membership.membership_type else None
    
    return {
        "valid_access": True,
        "membership_id": active_membership.id,
        "membership_type": active_membership.membership_type.name if active_membership.membership_type else active_membership.type,
        "expires_at": active_membership.end_date,
        "accesses_remaining": accesses_remaining
    }
