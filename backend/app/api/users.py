from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserUpdatePermissions
from app.repositories.user_repository import UserRepository
from app.core.dependencies import require_permission
from app.enums.permission import Permission
from app.core.security import get_effective_permissions

router = APIRouter(prefix="/users", tags=["users"])

_admin_only = require_permission(Permission.MANAGE_USERS)


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _=Depends(_admin_only),
):
    return UserRepository.get_all(db)


@router.post("/", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _=Depends(_admin_only),
):
    if UserRepository.get_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="نام کاربری تکراری است")
    return UserRepository.create(
        db=db,
        username=data.username,
        password=data.password,
        full_name=data.full_name,
        role=data.role,
        department=data.department,
        extra_permissions=data.extra_permissions,
        national_id=data.national_id,
        birth_date=data.birth_date,
        phone=data.phone,
        address=data.address,
    )


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _=Depends(_admin_only),
):
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    return UserRepository.update(db, user, data.model_dump(exclude_none=True))


@router.patch("/{user_id}/permissions", response_model=UserResponse)
def update_permissions(
    user_id: int,
    data: UserUpdatePermissions,
    db: Session = Depends(get_db),
    _=Depends(_admin_only),
):
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    return UserRepository.update_permissions(db, user, data.extra_permissions)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(_admin_only),
):
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    return UserRepository.set_active(db, user, False)


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(_admin_only),
):
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    return UserRepository.set_active(db, user, True)


class AdminResetPassword(BaseModel):
    new_password: str


@router.patch("/{user_id}/reset-password")
def admin_reset_password(
    user_id: int,
    data: AdminResetPassword,
    db: Session = Depends(get_db),
    _=Depends(_admin_only),
):
    from app.core.security import hash_password
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="رمز عبور باید حداقل ۶ کاراکتر باشد")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "رمز عبور تغییر کرد"}


@router.get("/me/permissions")
def my_permissions(current_user=Depends(require_permission(Permission.VIEW_REPORTS))):
    return {
        "role": current_user.role,
        "permissions": get_effective_permissions(
            current_user.role,
            current_user.extra_permissions or [],
        ),
    }
