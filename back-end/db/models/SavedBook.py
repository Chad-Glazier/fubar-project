from typing import Self

from db.persisted_model import PersistedModel

class SavedBook(PersistedModel):
	id: str
	user_id: str
	book_id: str

	@classmethod
	def save_for_user(cls, user_id: str, book_id: str) -> "SavedBook":
		existing = cls.get_by_primary_key(user_id + book_id)
		if existing != None:
			return existing

		return cls.create(
			id=user_id + book_id,
			user_id=user_id,
			book_id=book_id,
		)

	@classmethod
	def remove_for_user(cls, user_id: str, book_id: str) -> None:
		existing = cls.get_by_primary_key(user_id + book_id)
		if existing != None:
			existing.delete()

	@classmethod
	def get_saved_for_user(cls, user_id: str) -> list[Self]:
		return list(cls.get_where(user_id=user_id))
