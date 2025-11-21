from db.models.UserReview import UserReview
from db.recommend import recommend_for_user

def test_cold_start_returns_popular_books():
    # create reviews for books b1..b3
    tmp_reviews = [
		UserReview(id="r1", user_id="X", book_id="b1", rating=5.0),
		UserReview(id="r2", user_id="Y", book_id="b2", rating=4.0),
		UserReview(id="r3", user_id="Z", book_id="b1", rating=3.0),
		UserReview(id="r4", user_id="Z", book_id="b3", rating=5.0),
	]
    for review in tmp_reviews:
        review.put()

    # For a new user with no reviews, expect top by average rating: b3 (5.0), then b1 (4.0), then b2 (4.0 but fewer counts)
    recs = recommend_for_user("NEW_USER", n_recs=3)
    assert len(recs) >= 1
    top_book, _ = recs[0]
    assert top_book == "b3"
    
    for review in tmp_reviews:
        review.delete()
