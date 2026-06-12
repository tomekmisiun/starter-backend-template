import pytest
from fastapi import HTTPException

from app.core.upload_metadata import (
    validate_content_type_format,
    validate_upload_filename,
)


def test_validate_upload_filename_rejects_path_traversal():
    with pytest.raises(HTTPException) as exc_info:
        validate_upload_filename("../invoice.pdf")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid filename"


def test_validate_upload_filename_normalizes_whitespace():
    assert validate_upload_filename("  invoice.pdf  ") == "invoice.pdf"


def test_validate_content_type_format_rejects_invalid_mime():
    with pytest.raises(HTTPException) as exc_info:
        validate_content_type_format("not-a-mime")

    assert exc_info.value.status_code == 400
