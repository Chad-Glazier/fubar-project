"""Compatibility shim: re-export models from the `db.models` package.

Older code imported `db.models.User` or `from db.models import User`.
This file keeps that import path working while the real implementations
live in `db/models/*.py`.
"""

from .models.User import User
from .models.Book import Book
from .models.UserReview import UserReview

__all__ = ["User", "Book", "UserReview"]




