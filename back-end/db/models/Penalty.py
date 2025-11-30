from db.persisted_model import PersistedModel
from pydantic import Field

class Penalty(PersistedModel):
    id: str | None = None
    user_id: str
    penalty_type: str
    reason: str
    duration_days: int = Field(..., ge=1)
