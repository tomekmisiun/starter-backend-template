from dataclasses import dataclass
from uuid import uuid4

import boto3
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.uploaded_file import UploadedFile
from app.models.user import User


@dataclass(frozen=True)
class StoredObject:
    object_key: str
    size_bytes: int


class S3StorageProvider:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region_name,
        )

    def upload_file(
        self,
        *,
        object_key: str,
        body: bytes,
        content_type: str,
    ) -> None:
        self.client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=object_key,
            Body=body,
            ContentType=content_type,
        )


class StorageService:
    def __init__(self, provider: S3StorageProvider | None = None):
        self.provider = provider or S3StorageProvider()

    def upload(
        self,
        *,
        owner: User,
        file: UploadFile,
        db: Session,
    ) -> UploadedFile:
        validate_content_type(file.content_type)
        body = read_upload_body(file)
        validate_file_size(len(body))

        object_key = build_object_key(owner.id, file.filename or "upload")

        self.provider.upload_file(
            object_key=object_key,
            body=body,
            content_type=file.content_type or "application/octet-stream",
        )

        uploaded_file = UploadedFile(
            owner_id=owner.id,
            object_key=object_key,
            filename=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
            size_bytes=len(body),
        )

        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)

        return uploaded_file


def get_storage_service() -> StorageService:
    return StorageService()


def validate_content_type(content_type: str | None) -> None:
    allowed_content_types = {
        value.strip()
        for value in settings.upload_allowed_content_types.split(",")
        if value.strip()
    }

    if content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )


def validate_file_size(size_bytes: int) -> None:
    if size_bytes > settings.upload_max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File too large",
        )


def read_upload_body(file: UploadFile) -> bytes:
    return file.file.read()


def build_object_key(owner_id: int, filename: str) -> str:
    safe_filename = filename.replace("/", "_").replace("\\", "_")
    return f"uploads/{owner_id}/{uuid4().hex}-{safe_filename}"
