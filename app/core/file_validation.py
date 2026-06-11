from dataclasses import dataclass

from fastapi import HTTPException, status

from app.core.config import settings


CONTENT_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    "application/pdf": (b"%PDF",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/jpeg": (b"\xff\xd8\xff",),
}


@dataclass(frozen=True)
class MalwareScanResult:
    clean: bool
    detail: str


def sniff_content_type(body: bytes) -> str | None:
    for content_type, signatures in CONTENT_SIGNATURES.items():
        if any(body.startswith(signature) for signature in signatures):
            return content_type

    return None


def validate_declared_content_type(content_type: str | None) -> None:
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


def validate_content_sniff(declared_content_type: str, body: bytes) -> None:
    sniffed_content_type = sniff_content_type(body)

    if sniffed_content_type != declared_content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not match declared content type",
        )


def run_malware_scan(body: bytes, filename: str) -> MalwareScanResult:
    if not settings.upload_malware_scan_enabled:
        return MalwareScanResult(clean=True, detail="malware_scan_disabled")

    return scan_uploaded_file(body, filename)


def scan_uploaded_file(body: bytes, filename: str) -> MalwareScanResult:
    """Integration point for external malware scanners in downstream projects."""

    _ = body, filename
    return MalwareScanResult(clean=True, detail="malware_scan_passed")


def ensure_malware_scan_is_clean(scan_result: MalwareScanResult) -> None:
    if scan_result.clean:
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="File failed malware scanning",
    )
