from pydantic import Field

from db.persisted_model import PersistedModel

class UserReview(PersistedModel):
    id: str
    user_id: str
    book_id: str
    rating: int = Field(..., ge=0, le=10)
    text: str = Field(default = "")

