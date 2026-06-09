from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums.user_role import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=UserRole.CASHIER,
    )

    department: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    national_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    birth_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(String(256), nullable=True)

    extra_permissions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
