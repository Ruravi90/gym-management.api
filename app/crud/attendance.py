from sqlalchemy.orm import Session
from ..models.attendance import Attendance
from ..schemas.attendance import AttendanceCreate, AttendanceUpdate
from datetime import datetime

def get_attendance(db: Session, attendance_id: int):
    return db.query(Attendance).filter(Attendance.id == attendance_id).first()

def get_attendances_by_client(db: Session, client_id: int):
    return db.query(Attendance).filter(Attendance.client_id == client_id).all()

def create_attendance(db: Session, attendance: AttendanceCreate):
    db_attendance = Attendance(
        client_id=attendance.client_id,
        check_in=attendance.check_in,
        check_out=attendance.check_out,
        date=attendance.date
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def update_attendance_checkout(db: Session, attendance_id: int, check_out: datetime):
    db_attendance = get_attendance(db, attendance_id)
    if db_attendance:
        db_attendance.check_out = check_out
        db.commit()
        db.refresh(db_attendance)
    return db_attendance
