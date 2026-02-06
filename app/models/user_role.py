from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    RECEPTIONIST = "receptionist"
    MANAGER = "manager"
    MEMBER = "member"  # Regular member who uses the gym
    SUPER_ADMIN = "super_admin"