from datetime import datetime
from pydantic import Field
from db.persisted_model import PersistedModel


class AuditLog(PersistedModel):
    id: str
    admin_id: str
    action: str
    target_id: str | None = None
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())

    @classmethod
    def new_id(cls) -> str:
        return cls.generate_primary_key()
