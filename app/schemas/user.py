from enum import StrEnum

from pydantic import BaseModel, EmailStr


class UserRole(StrEnum):
    user = "user"
    admin = "admin"
    platform_admin = "platform_admin"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str

    class Config:
        from_attributes = True


class UserSelfUpdate(BaseModel):
    email: EmailStr | None = None


class UserAdminUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None
    role: UserRole | None = None
