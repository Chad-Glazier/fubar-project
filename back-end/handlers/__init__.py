from .saved_books import saved_book_router
from .user import user_router
from .search import search_router
from .recommendations import recommend_router
from .book_details import book_router
from .review import review_router
from .profile_pictures import profile_pictures_router
from .admin import admin_router
from .sentiment import sentiment_router

__all__ = [
    "user_router",
    "saved_book_router",
    "search_router",
    "recommend_router",
    "book_router",
    "review_router",
    "admin_router",
    "sentiment_router",
	"profile_pictures_router"
]

ROUTERS = (
    user_router,
    saved_book_router,
    search_router,
    recommend_router,
    book_router,
    review_router,
    admin_router,
    sentiment_router,
	profile_pictures_router
)
