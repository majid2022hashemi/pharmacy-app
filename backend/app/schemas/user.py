from pydantic import BaseModel, field_validator


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str
    department: str | None = None
    extra_permissions: list[str] = []
    national_id: str | None = None
    birth_date: str | None = None
    phone: str | None = None
    address: str | None = None

    @field_validator("national_id")
    @classmethod
    def validate_national_id(cls, v: str | None) -> str | None:
        if v is not None and (not v.isdigit() or len(v) != 10):
            raise ValueError("کد ملی باید ۱۰ رقم باشد")
        return v


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: str | None = None
    department: str | None = None
    national_id: str | None = None
    birth_date: str | None = None
    phone: str | None = None
    address: str | None = None


class UserUpdatePermissions(BaseModel):
    extra_permissions: list[str]


class ResetPasswordRequest(BaseModel):
    username: str
    national_id: str
    birth_date: str
    new_password: str


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    department: str | None
    national_id: str | None
    phone: str | None
    address: str | None
    extra_permissions: list[str]
    is_active: bool

    model_config = {"from_attributes": True}
