import os
from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.enums.user_role import UserRole
from app.enums.permission import Permission

SECRET_KEY = os.environ.get("SECRET_KEY", "pharmacy-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

# مجوزهای پیش‌فرض هر نقش
ROLE_DEFAULT_PERMISSIONS: dict[str, list[str]] = {
    UserRole.ADMIN: [p.value for p in Permission],
    UserRole.PHARMACIST: [
        Permission.CREATE_PURCHASE,
        Permission.CREATE_SALE,
        Permission.CHANGE_PRICE,
        Permission.MANAGE_INVENTORY,
        Permission.VIEW_REPORTS,
        Permission.MANAGE_RETURNS,
    ],
    UserRole.OTC: [
        Permission.CREATE_SALE,
        Permission.VIEW_REPORTS,
    ],
    UserRole.PRESCRIPTION: [
        Permission.CREATE_SALE,
        Permission.VIEW_REPORTS,
    ],
    UserRole.COSMETICS: [
        Permission.CREATE_SALE,
        Permission.VIEW_REPORTS,
    ],
    UserRole.CASHIER: [
        Permission.CREATE_SALE,
        Permission.VIEW_REPORTS,
    ],
    UserRole.WAREHOUSE: [
        Permission.CREATE_PURCHASE,
        Permission.MANAGE_INVENTORY,
        Permission.VIEW_REPORTS,
        Permission.MANAGE_RETURNS,
    ],
    UserRole.MEDICAL_EQUIPMENT: [
        Permission.CREATE_SALE,
        Permission.VIEW_REPORTS,
    ],
}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_effective_permissions(role: str, extra_permissions: list[str]) -> list[str]:
    defaults = ROLE_DEFAULT_PERMISSIONS.get(role, [])
    return list(set([p.value if isinstance(p, Permission) else p for p in defaults] + extra_permissions))
