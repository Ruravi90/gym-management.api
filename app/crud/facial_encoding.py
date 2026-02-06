from sqlalchemy.orm import Session
from ..models.facial_encoding import FacialEncoding
from ..schemas.facial_encoding import FacialEncodingCreate

def get_facial_encoding_by_client(db: Session, client_id: int):
    """Get facial encoding for a specific client"""
    return db.query(FacialEncoding).filter(FacialEncoding.client_id == client_id).first()

def create_facial_encoding(db: Session, facial_encoding: FacialEncodingCreate, encoding_data: bytes):
    """Create a new facial encoding"""
    db_facial_encoding = FacialEncoding(
        client_id=facial_encoding.client_id,
        encoding_data=encoding_data
    )
    db.add(db_facial_encoding)
    db.commit()
    db.refresh(db_facial_encoding)
    return db_facial_encoding

def update_facial_encoding(db: Session, client_id: int, encoding_data: bytes):
    """Update facial encoding for a client"""
    db_facial_encoding = get_facial_encoding_by_client(db, client_id)
    if db_facial_encoding:
        db_facial_encoding.encoding_data = encoding_data
        db.commit()
        db.refresh(db_facial_encoding)
        return db_facial_encoding
    return None

def delete_facial_encoding(db: Session, client_id: int):
    """Delete facial encoding for a client"""
    db_facial_encoding = get_facial_encoding_by_client(db, client_id)
    if db_facial_encoding:
        db.delete(db_facial_encoding)
        db.commit()
        return db_facial_encoding
    return None