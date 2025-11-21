from db.models.UserReview import UserReview
from db.recommend import recommend_for_user


def setup_module(module):
    UserReview._drop_table()


def teardown_module(module):
    UserReview._drop_table()


def test_cold_start_returns_popular_books():
    # create reviews for books b1..b3
    r1 = UserReview(id="r1", user_id="X", book_id="b1", rating=5.0)
    r1.post()
    r2 = UserReview(id="r2", user_id="Y", book_id="b2", rating=4.0)
    r2.post()
    r3 = UserReview(id="r3", user_id="Z", book_id="b1", rating=3.0)
    r3.post()
    r4 = UserReview(id="r4", user_id="Z", book_id="b3", rating=5.0)
    r4.post()

    # For a new user with no reviews, expect top by average rating: b3 (5.0), then b1 (4.0), then b2 (4.0 but fewer counts)
    recs = recommend_for_user("NEW_USER", n_recs=3)
    assert len(recs) >= 1
    top_book, top_score = recs[0]
    assert top_book == "b3"
