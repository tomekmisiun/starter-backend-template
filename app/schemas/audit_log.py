from datetime import datetime

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: int
    admin_id: int
    action: str
    target_user_id: int | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
