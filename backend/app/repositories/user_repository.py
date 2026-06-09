from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


class UserRepository:

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_all(db: Session) -> list[User]:
        return db.query(User).order_by(User.id).all()

    @staticmethod
    def reset_password_by_identity(
        db: Session,
        username: str,
        national_id: str,
        birth_date: str,
        new_password: str,
    ) -> bool:
        user = (
            db.query(User)
            .filter(
                User.username == username,
                User.national_id == national_id,
                User.birth_date == birth_date,
                User.is_active == True,
            )
            .first()
        )
        if user is None:
            return False
        user.password_hash = hash_password(new_password)
        db.commit()
        return True

    @staticmethod
    def create(
        db: Session,
        username: str,
        password: str,
        full_name: str,
        role: str,
        department: str | None = None,
        extra_permissions: list[str] | None = None,
        national_id: str | None = None,
        birth_date: str | None = None,
        phone: str | None = None,
        address: str | None = None,
    ) -> User:
        user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            department=department,
            extra_permissions=extra_permissions or [],
            national_id=national_id,
            birth_date=birth_date,
            phone=phone,
            address=address,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: User, data: dict) -> User:
        for field, value in data.items():
            if value is not None and hasattr(user, field):
                setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_permissions(
        db: Session,
        user: User,
        extra_permissions: list[str],
    ) -> User:
        user.extra_permissions = extra_permissions
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def set_active(db: Session, user: User, is_active: bool) -> User:
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def count(db: Session) -> int:
        return db.query(User).count()
