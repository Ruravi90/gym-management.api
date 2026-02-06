from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db
from app.services.facial_recognition import FacialRecognitionService
from app.middleware.security import limiter, file_upload_limits

router = APIRouter()
face_service = FacialRecognitionService()

@router.post("/verify")
@limiter.limit(file_upload_limits)
async def verify_identity(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Verify identity using facial recognition.
    Returns client information if recognized.
    """
    content = await file.read()

    try:
        client_id = face_service.identify_client(content, db)
        if client_id is None:
            raise HTTPException(status_code=404, detail="Client not recognized")

        client = crud.client.get_client(db, client_id=client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found in database")

        # Return client info without sensitive data
        return {
            "client_id": client.id,
            "name": client.name,
            "email": client.email,
            "recognized": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

@router.post("/register/{client_id}")
@limiter.limit(file_upload_limits)
async def register_client_face(request: Request, client_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Register a face for a specific client.
    """
    client = crud.client.get_client(db, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    content = await file.read()
    try:
        success = face_service.register_face(db, client_id, content)
        if success:
            return {"status": "success", "message": "Face registered successfully", "client_id": client_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to register face")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")