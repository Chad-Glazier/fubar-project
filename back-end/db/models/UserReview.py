from db.persisted_model import PersistedModel


class UserReview(PersistedModel):
    id: str
    user_id: str
    book_id: str
    rating: float  # e.g., 1–5
