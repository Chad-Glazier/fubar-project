from pydantic import Field
from db.persisted_model import PersistedModel


class Penalty(PersistedModel):
    id: str
    user_id: str
    penalty_type: str
    reason: str
    duration_days: int = 0
    active: bool = True

    @classmethod
    def new_id(cls):
        return cls.generate_primary_key()
