from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from typing import List
from datetime import datetime, timezone
from app import crud, schemas, models
from app.middleware.security import limiter, file_upload_limits
from app.services.facial_recognition import FacialRecognitionService
from app.utils.auth import get_current_user
from app.models.user import User as UserModel


router = APIRouter()

_face_service = None

def get_face_service() -> FacialRecognitionService:
    global _face_service
    if _face_service is None:
        _face_service = FacialRecognitionService()
    return _face_service

@router.post("/", response_model=schemas.Attendance)
async def create_attendance(attendance: schemas.AttendanceCreate, current_user: UserModel = Depends(get_current_user)):
    # Verify client exists
    client = await crud.client.get_client(client_id=attendance.client_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
    return await crud.attendance.create_attendance(
        attendance.dict(),
        user_id=current_user.id,
        ip_address=None,  # Will be populated later with request info
        user_agent=None   # Will be populated later with request info
    )

@router.get("/client/{client_id}", response_model=List[schemas.Attendance])
async def read_attendances(client_id: int):
    return await crud.attendance.get_attendance_by_client(client_id=client_id)

@router.post("/check-in", response_model=schemas.Attendance)
@limiter.limit("60 per minute")  # Higher limit for check-in since it's used frequently
async def check_in(request: Request, file: UploadFile = File(...)):
    content = await file.read()
    client_id = await get_face_service().identify_client(content)

    if not client_id:
        raise HTTPException(status_code=400, detail="Face not recognized")

    # Check for existing open attendance (check-in without check-out)
    last_attendance = await models.Attendance.filter(client_id=client_id).order_by("-check_in_time").first()

    if last_attendance and last_attendance.check_out_time is None:
        # Check out
        attendance = await crud.attendance.update_attendance_checkout(last_attendance.id, datetime.now(timezone.utc))
    else:
        # Check in
        attendance_data = {
            "client_id": client_id,
            "device_id": None  # Will be set by the model automatically
        }
        # For facial recognition, we'll use a system user or no user for audit logging
        attendance = await crud.attendance.create_attendance(
            attendance_data,
            user_id=None,  # Facial recognition doesn't have a logged-in user
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

    return attendance

@router.post("/manual/{client_id}", response_model=schemas.Attendance)
async def check_in_manual(client_id: int, current_user: UserModel = Depends(get_current_user)):
    # Verify client exists
    client = await crud.client.get_client(client_id=client_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")

    last_attendance = await models.Attendance.filter(client_id=client_id).order_by("-check_in_time").first()

    if last_attendance and last_attendance.check_out_time is None:
        # Check out
        attendance = await crud.attendance.update_attendance_checkout(last_attendance.id, datetime.now(timezone.utc))
    else:
        # Check in
        attendance_data = {
            "client_id": client_id,
            "device_id": None  # Will be set by the model automatically
        }
        attendance = await crud.attendance.create_attendance(
            attendance_data,
            user_id=current_user.id,
            ip_address=None,  # Will be populated later with request info
            user_agent=None   # Will be populated later with request info
        )

    return attendance
