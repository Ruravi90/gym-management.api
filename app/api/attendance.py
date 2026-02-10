from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from typing import List
from datetime import datetime
from app import crud, schemas, models
from app.middleware.security import limiter, file_upload_limits
from app.services.facial_recognition import FacialRecognitionService
from app.database import get_db

router = APIRouter()

face_service = FacialRecognitionService()

@router.post("/", response_model=schemas.Attendance)
async def create_attendance(attendance: schemas.AttendanceCreate):
    # Verify client exists
    client = await crud.client.get_client(client_id=attendance.client_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
    return await crud.attendance.create_attendance(attendance=attendance)

@router.get("/client/{client_id}", response_model=List[schemas.Attendance])
async def read_attendances(client_id: int):
    return await crud.attendance.get_attendances_by_client(client_id=client_id)

@router.post("/check-in", response_model=schemas.Attendance)
@limiter.limit("60 per minute")  # Higher limit for check-in since it's used frequently
async def check_in(request: Request, file: UploadFile = File(...)):
    content = await file.read()
    client_id = await face_service.identify_client(content)

    if not client_id:
        raise HTTPException(status_code=400, detail="Face not recognized")

    # Check for existing open attendance (check-in without check-out)
    last_attendance = await models.Attendance.filter(client_id=client_id).order_by("-check_in").first()

    if last_attendance and last_attendance.check_out is None:
        # Check out
        attendance = await crud.attendance.update_attendance_checkout(last_attendance.id, datetime.utcnow())
    else:
        # Check in
        attendance_create = schemas.AttendanceCreate(
            client_id=client_id,
            check_in=datetime.utcnow(),
            date=datetime.utcnow()
        )
        attendance = await crud.attendance.create_attendance(attendance=attendance_create)

    return attendance
@router.post("/manual/{client_id}", response_model=schemas.Attendance)
async def check_in_manual(client_id: int):
    # Verify client exists
    client = await crud.client.get_client(client_id=client_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")

    last_attendance = await models.Attendance.filter(client_id=client_id).order_by("-check_in").first()

    if last_attendance and last_attendance.check_out is None:
        # Check out
        attendance = await crud.attendance.update_attendance_checkout(last_attendance.id, datetime.utcnow())
    else:
        # Check in
        attendance_create = schemas.AttendanceCreate(
            client_id=client_id,
            check_in=datetime.utcnow(),
            date=datetime.utcnow()
        )
        attendance = await crud.attendance.create_attendance(attendance=attendance_create)

    return attendance
