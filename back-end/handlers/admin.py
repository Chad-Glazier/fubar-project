from fastapi import APIRouter, HTTPException, Request
from http import HTTPStatus

from db.models.User import User
from db.models.UserReview import UserReview
from db.models.Book import Book
from db.models.Penalty import Penalty
from db.models.AuditLog import AuditLog

admin_router = APIRouter(prefix="/admin", tags=["admin"])

# -------------------------------------------------------------------------
# TEMPORARY: Disable admin requirement 
##def require_admin(req: Request) -> User:
##    user = User.from_session(req)
##    if user is None or not getattr(user, "is_admin", False):
##        raise HTTPException(
##            status_code=HTTPStatus.UNAUTHORIZED,
##            detail="Administrator access required."
   ##     )
 ##   return user
# -------------------------------------------------------------------------

def require_admin(req: Request):
    # TEMPORARY: All users allowed. No login required.
    return True

# US11 – Admin dashboard

@admin_router.get("/dashboard")
async def get_dashboard(req: Request):
    # Admin disabled72794
    total_books = len(list(Book.get_all()))
    total_reviews = len(list(UserReview.get_all()))
    total_reports = len(list(UserReview.get_where(reported=True)))
    total_penalties = len(list(Penalty.get_all()))


    return {
        "total_books": total_books,
        "total_reviews": total_reviews,
        "flagged_reviews": total_reports,
        "active_penalties": total_penalties,
    }

# US8 – User reports a review

@admin_router.post("/report/{review_id}")
async def report_review(review_id: str, req: Request):
    user = User.from_session(req)  # Still allow normal user
    if user is None:
        raise HTTPException(401, "Login required.")

    review = UserReview.get_by_primary_key(review_id)
    if review is None:
        raise HTTPException(404, "Review not found.")

    review.reported = True
    review.put()
    return {"status": "review_reported"}

# US12 – View all flagged reviews

@admin_router.get("/flagged")
async def get_flagged_reviews(req: Request):
    # Admin disabled
    return list(UserReview.get_where(reported=True))

# US12 – Delete a flagged review

@admin_router.delete("/flagged/{review_id}")
async def delete_flagged_review(review_id: str, req: Request):
    # Admin disabled
    review = UserReview.get_by_primary_key(review_id)
    if review is None:
        raise HTTPException(404, "Review not found.")

    review.delete()

    AuditLog(
        action="delete_review",
        admin_id="TEMP_ADMIN",
        target_id=review_id
    ).put()

    return {"status": "review_deleted"}
# US13 – Apply a penalty to a user

@admin_router.post("/penalty/{user_id}")
async def apply_penalty(user_id: str, data: dict, req: Request):
    # Admin disabled
    user = User.get_by_primary_key(user_id)
    if user is None:
        raise HTTPException(404, "User not found.")

    penalty = Penalty(
        user_id=user_id,
        penalty_type=data["type"],
        reason=data["reason"],
        duration_days=data["duration"]
    )
    penalty.put()

    AuditLog(
        action="apply_penalty",
        admin_id="TEMP_ADMIN",
        target_id=user_id
    ).put()

    return {"status": "penalty_applied"}
# US14 – Book creation
@admin_router.post("/books")
async def create_book(data: dict, req: Request):
    # Admin disabled
    book = Book(**data)
    book.post()
    return book
# US14 – Book editing

@admin_router.patch("/books/{book_id}")
async def update_book(book_id: str, updates: dict, req: Request):
    # Admin disabled
    book = Book.get_by_primary_key(book_id)
    if book is None:
        raise HTTPException(404, "Book not found.")

    for k, v in updates.items():
        setattr(book, k, v)

    book.put()
    return {"status": "book_updated", "book": book}


# US14 – Merge books

@admin_router.post("/books/merge")
async def merge_books(data: dict, req: Request):
    # Admin disabled
    src = Book.get_by_primary_key(data["source"])
    dst = Book.get_by_primary_key(data["target"])

    if src is None or dst is None:
        raise HTTPException(404, "One or both books not found.")

    # move reviews
    for r in UserReview.get_where(book_id=src.id):
        r.book_id = dst.id
        r.put()

    src.delete()

    AuditLog(
        action="merge_books",
        admin_id="TEMP_ADMIN",
        target_id=f"{src.id}->{dst.id}"
    ).put()

    return {"status": "merged", "target": dst.id}

# US15 – View audit logs

@admin_router.get("/audit")
async def get_audit(req: Request):
    # Admin disabled
    return AuditLog.get_all()
