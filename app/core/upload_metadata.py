import re

from fastapi import HTTPException, status

MAX_UPLOAD_FILENAME_LENGTH = 255
CONTENT_TYPE_PATTERN = re.compile(r"^[a-zA-Z0-9!#$&\-^_.+]+/[a-zA-Z0-9!#$&\-^_.+]+$")


def validate_upload_filename(filename: str) -> str:
    normalized_filename = filename.strip()

    if not normalized_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    if len(normalized_filename) > MAX_UPLOAD_FILENAME_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is too long",
        )

    if any(
        forbidden in normalized_filename
        for forbidden in ("\x00", "/", "\\", "..")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename",
        )

    return normalized_filename


def validate_content_type_format(content_type: str) -> str:
    normalized_content_type = content_type.strip().lower()

    if not CONTENT_TYPE_PATTERN.fullmatch(normalized_content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid content type format",
        )

    return normalized_content_type
