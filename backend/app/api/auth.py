from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import ResetPasswordRequest
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(db, data.username, data.password)


@router.get("/check-username/{username}")
def check_username(username: str, db: Session = Depends(get_db)):
    user = UserRepository.get_by_username(db, username)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد",
        )
    return {"found": True}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز عبور باید حداقل ۶ کاراکتر باشد",
        )
    ok = UserRepository.reset_password_by_identity(
        db,
        username=data.username,
        national_id=data.national_id,
        birth_date=data.birth_date,
        new_password=data.new_password,
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="اطلاعات وارد شده صحیح نیست",
        )
    return {"message": "رمز عبور با موفقیت تغییر کرد"}
