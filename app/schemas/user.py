from pydantic import BaseModel, EmailStr


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
    role: str | None = None
