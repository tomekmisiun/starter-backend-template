from datetime import datetime

from pydantic import BaseModel


class UploadedFileRead(BaseModel):
    id: int
    owner_id: int
    object_key: str
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
