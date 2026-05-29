from fastapi import APIRouter, Depends

from app.api.dependencies.auth import require_role
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("")
def admin_panel(
    current_user: User = Depends(require_role("admin")),
):
    return {
        "message": "Welcome admin",
        "email": current_user.email,
    }