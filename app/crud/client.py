from sqlalchemy.orm import Session
from ..models.client import Client
from ..schemas.client import ClientCreate, ClientUpdate
from ..utils.auth import hash_password

def get_client(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first()

def get_client_by_email(db: Session, email: str):
    return db.query(Client).filter(Client.email == email).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Client).offset(skip).limit(limit).all()


def search_clients(db: Session, search_term: str, skip: int = 0, limit: int = 100):
    """Search clients by name or email"""
    query = db.query(Client)

    # Search by name or email (case insensitive)
    search_pattern = f"%{search_term}%"
    query = query.filter(
        (Client.name.ilike(search_pattern)) |
        (Client.email.ilike(search_pattern))
    )

    return query.offset(skip).limit(limit).all()

def create_client(db: Session, client: ClientCreate):
    # Password is optional for clients. Only hash/store if provided.
    hashed_password = None
    if getattr(client, 'password', None):
        hashed_password = hash_password(client.password)

    db_client = Client(
        email=client.email,
        name=client.name,
        phone=client.phone,
        membership_type=client.membership_type,
        hashed_password=hashed_password
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def update_client(db: Session, client_id: int, client_update: ClientUpdate):
    db_client = get_client(db, client_id)
    if db_client:
        update_data = client_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_client, field, value)
        db.commit()
        db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: int):
    db_client = get_client(db, client_id)
    if db_client:
        db.delete(db_client)
        db.commit()
    return db_client