print("Loading schemas __init__.py...")
from .user import User, UserCreate, UserUpdate
from .client import Client, ClientCreate, ClientUpdate
from .membership import Membership, MembershipCreate, MembershipUpdate, MembershipStatistics, MembershipType, MembershipTypeCreate, MembershipTypeUpdate, PunchUsage
from .attendance import Attendance, AttendanceCreate, AttendanceUpdate
from .gym_class import GymClass, GymClassCreate, GymClassUpdate
from .auth import UserLogin, Token, TokenData, UserRegister
from .audit_log import AuditLog, AuditLogCreate, AuditLogUpdate, ActionTypeEnum

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "Client",
    "ClientCreate",
    "ClientUpdate",
    "Membership",
    "MembershipCreate",
    "MembershipUpdate",
    "MembershipStatistics",
    "MembershipType",
    "MembershipTypeCreate",
    "MembershipTypeUpdate",
    "PunchUsage",
    "Attendance",
    "AttendanceCreate",
    "AttendanceUpdate",
    "GymClass",
    "GymClassCreate",
    "GymClassUpdate",
    "UserLogin",
    "Token",
    "TokenData",
    "UserRegister",
    "AuditLog",
    "AuditLogCreate",
    "AuditLogUpdate",
    "ActionTypeEnum"
]