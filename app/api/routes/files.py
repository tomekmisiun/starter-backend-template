from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.openapi import PROTECTED_ERROR_RESPONSES
from app.db.session import get_db
from app.models.user import User
from app.schemas.file import UploadedFileRead
from app.services.storage_service import get_storage_service


router = APIRouter(prefix="/files", tags=["files"])


@router.post(
    "/upload",
    response_model=UploadedFileRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
    description=(
        "Authenticated multipart upload with size and content-type validation. "
        "Stores metadata in PostgreSQL and the object in S3-compatible storage."
    ),
    responses=PROTECTED_ERROR_RESPONSES,
)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_storage_service().upload(
        owner=current_user,
        file=file,
        db=db,
    )
