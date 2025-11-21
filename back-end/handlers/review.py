from fastapi import APIRouter, HTTPException, Request, Response
from http import HTTPStatus
from pydantic import BaseModel, Field

from db.models.UserReview import UserReview
from db.models.User import User
from db.models.Book import Book

review_router = APIRouter(prefix = "/review")


###############################################################################
# 
# The types that will be used by this router are defined below.
#

class ReviewDetails(BaseModel):
	rating: int = Field(..., ge=0, le=10)
	text: str = Field(default = "")

###############################################################################
# 
# The request handlers are defined below.
#

#
# Let users view a specific review (all reviews are public)
#
@review_router.get("/{review_id}")
async def get_review(review_id: str) -> UserReview:
	review = UserReview.get_by_primary_key(review_id)
	if review == None:
		raise HTTPException(
			status_code = HTTPStatus.NOT_FOUND,
			detail = f"No review with ID {review_id} was found."
		)
	
	return review

#
# Let users view all reviews that match some search parameters.
#
@review_router.get("/")
async def get_reviews(
	author_display_name: str | None = None,
	author_id: str | None = None,
	book_id: str | None = None,
	require_text: bool | None = None,
	limit: int = 20
) -> list[UserReview]:
	
	if author_display_name != None:
		author = User.get_first_where(display_name = author_display_name)
		if author == None:
			raise HTTPException(
				status_code = 404,
				detail = f"No author named {author_display_name} was found."
			)
		author_id = author.id

	if book_id != None:
		book = Book.get_by_primary_key(book_id)
		if book == None:
			raise HTTPException(
				status_code = 404,
				detail = f"No book with ID {book_id} was found."
			)

	if author_id != None and book_id != None:
		reviews = UserReview.get_where(book_id = book_id, user_id = author_id)
	elif author_id != None:
		reviews = UserReview.get_where(user_id = author_id)
	elif book_id != None:
		reviews = UserReview.get_where(book_id = book_id)
	else:
		reviews = UserReview.get_all()

	results: list[UserReview] = []
	result_count = 0

	if require_text:
		for review in reviews:
			if review.text == "":
				continue

			results.append(review)
			result_count += 1

			if result_count >= limit:
				break
	else:
		for review in reviews:
			results.append(review)
			result_count += 1

			if result_count >= limit:
				break

	return results

#
# Let users create a review.
#
@review_router.put("/{book_id}")
async def post_review(
	book_id: str, 
	review: ReviewDetails, 
	req: Request, 
	resp: Response
) -> UserReview:
	user = User.from_session(req)
	if user == None:
		raise HTTPException(
			status_code = HTTPStatus.UNAUTHORIZED,
			detail = "You must be logged in to post a review."
		)
	
	book = Book.get_by_primary_key(book_id)
	if book == None:
		raise HTTPException(
			status_code = 404,
			detail = f"No book with ID {book_id} was found."
		)
	
	new_review = UserReview(
		# A user can only have one review per book, so this field
		# should be unique. Redundant requests to this endpoint will
		# thus be treated as updates.
		id = user.id + book_id,
		user_id = user.id,
		book_id = book_id,
		rating = review.rating,
		text = review.text
	)
	new_review.put()

	resp.status_code = HTTPStatus.CREATED

	return new_review

