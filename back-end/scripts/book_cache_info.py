"""
Utility script to inspect the in-process Book cache metrics.

Usage:
    python -m scripts.book_cache_info
"""

from db.models.Book import Book


def main() -> None:
    stats = Book.cache_info()
    print("Book cache stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
