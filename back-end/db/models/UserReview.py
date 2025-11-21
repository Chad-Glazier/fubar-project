from pydantic import Field

from db.persisted_model import PersistedModel

class UserReview(PersistedModel):
    id: str
    user_id: str
    book_id: str
    rating: int = Field(..., ge=1, le=10)
