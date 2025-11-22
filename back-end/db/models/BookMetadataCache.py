from db.persisted_model import PersistedModel


class BookMetadataCache(PersistedModel):
	query: str
	book_id: str
