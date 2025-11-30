from db.persisted_model import PersistedModel

class AuditLog(PersistedModel):
    id: str | None = None
    action: str
    admin_id: str
    target_id: str
