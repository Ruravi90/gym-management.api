from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app import crud, models, schemas
from app.database import get_db
from app.services.facial_recognition import FacialRecognitionService
from app.utils.auth import get_current_user
from app.models.user import User as UserModel

router = APIRouter()
face_service = FacialRecognitionService()

@router.post("/", response_model=schemas.Client)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_client = crud.client.get_client_by_email(db, email=client.email)
    if db_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.client.create_client(db=db, client=client)

@router.get("/", response_model=List[schemas.Client])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    clients = crud.client.get_clients(db, skip=skip, limit=limit)
    return clients

@router.get("/search/", response_model=List[schemas.Client])
def search_clients(search: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    clients = crud.client.search_clients(db, search_term=search, skip=skip, limit=limit)
    return clients

@router.get("/{client_id}", response_model=schemas.Client)
def read_client(client_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_client = crud.client.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.put("/{client_id}", response_model=schemas.Client)
def update_client(client_id: int, client_update: schemas.ClientUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_client = crud.client.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return crud.client.update_client(db=db, client_id=client_id, client_update=client_update)

@router.delete("/{client_id}", response_model=schemas.Client)
def delete_client(client_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_client = crud.client.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return crud.client.delete_client(db=db, client_id=client_id)

@router.post("/{client_id}/face")
async def register_face(client_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    client = crud.client.get_client(db, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    content = await file.read()
    try:
        success = face_service.register_face(db, client_id, content)
        return {"status": "success", "message": "Face registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{client_id}/face")
def get_face_registration_status(client_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Check if client has registered their face"""
    client = crud.client.get_client(db, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    facial_encoding = crud.facial_encoding.get_facial_encoding_by_client(db, client_id=client_id)
    if facial_encoding:
        return {"registered": True, "message": "Face is registered"}
    else:
        return {"registered": False, "message": "Face is not registered"}

@router.delete("/{client_id}/face")
def remove_face_registration(client_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Remove face registration for a client"""
    client = crud.client.get_client(db, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    facial_encoding = crud.facial_encoding.delete_facial_encoding(db, client_id=client_id)
    if facial_encoding:
        return {"status": "success", "message": "Face registration removed"}
    else:
        raise HTTPException(status_code=404, detail="Face registration not found")