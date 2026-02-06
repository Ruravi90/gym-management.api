from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app import crud, schemas, models
from app.database import get_db
from app.middleware.security import limiter, file_upload_limits
from app.services.facial_recognition import FacialRecognitionService

router = APIRouter()

face_service = FacialRecognitionService()

@router.post("/", response_model=schemas.Attendance)
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    # Verify client exists
    client = crud.client.get_client(db, client_id=attendance.client_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
    return crud.attendance.create_attendance(db=db, attendance=attendance)

@router.get("/client/{client_id}", response_model=List[schemas.Attendance])
def read_attendances(client_id: int, db: Session = Depends(get_db)):
    return crud.attendance.get_attendances_by_client(db, client_id=client_id)

@router.post("/check-in", response_model=schemas.Attendance)
@limiter.limit("60 per minute")  # Higher limit for check-in since it's used frequently
async def check_in(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    client_id = face_service.identify_client(content, db)

    if not client_id:
        raise HTTPException(status_code=400, detail="Face not recognized")

    # Check for existing open attendance (check-in without check-out)
    # This logic is simplified; real logic might be more complex
    # For now, just create a new check-in

    # Or maybe if they Checked In recently, Check Out?
    # User requirements says "Control de asistencia"
    # I'll implement a toggle logic: If last record is Check In, Check Out. Else Check In.

    last_attendance = db.query(models.Attendance).filter(models.Attendance.client_id == client_id).order_by(models.Attendance.check_in.desc()).first()

    if last_attendance and last_attendance.check_out is None:
        # Check out
        attendance = crud.attendance.update_attendance_checkout(db, last_attendance.id, datetime.utcnow())
    else:
        # Check in
        attendance_create = schemas.AttendanceCreate(
            client_id=client_id,
            check_in=datetime.utcnow(),
            date=datetime.utcnow()
        )
        attendance = crud.attendance.create_attendance(db, attendance_create)

    return attendance
@router.post("/manual/{client_id}", response_model=schemas.Attendance)
async def check_in_manual(client_id: int, db: Session = Depends(get_db)):
    # Verify client exists
    client = crud.client.get_client(db, client_id=client_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")

    last_attendance = db.query(models.Attendance).filter(models.Attendance.client_id == client_id).order_by(models.Attendance.check_in.desc()).first()

    if last_attendance and last_attendance.check_out is None:
        # Check out
        attendance = crud.attendance.update_attendance_checkout(db, last_attendance.id, datetime.utcnow())
    else:
        # Check in
        attendance_create = schemas.AttendanceCreate(
            client_id=client_id,
            check_in=datetime.utcnow(),
            date=datetime.utcnow()
        )
        attendance = crud.attendance.create_attendance(db, attendance_create)

    return attendance
