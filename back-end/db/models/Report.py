from pydantic import Field
from db.persisted_model import PersistedModel


class Report(PersistedModel):
    id: str
    review_id: str
    user_id: str
    reason: str = Field(default="")
    text: str = Field(default="")

    @classmethod
    def new_id(cls):
        return cls.generate_primary_key()
