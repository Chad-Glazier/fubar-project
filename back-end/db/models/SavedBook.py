import uuid
from typing import Self

from db.persisted_model import PersistedModel

class SavedBook(PersistedModel):
    id: str
    user_id: str
    book_id: str

    @classmethod
    def save_for_user(cls, user_id: str, book_id: str) -> "SavedBook":
        existing = cls.get_first_where(user_id=user_id, book_id=book_id)
        if existing:
            return existing

        return cls.create(
            id=str(uuid.uuid4()),
            user_id=user_id,
            book_id=book_id,
        )

    @classmethod
    def remove_for_user(cls, user_id: str, book_id: str) -> None:
        for record in cls.get_where(user_id=user_id, book_id=book_id):
            record.delete()

    @classmethod
    def get_saved_for_user(cls, user_id: str) -> list[Self]:
        return list(cls.get_where(user_id=user_id))
