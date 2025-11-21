from db.models.UserReview import UserReview
from db.models.Book import Book
from db.recommend import recommend_for_user


def setup_module(module):
    # clear tables before test
    UserReview._drop_table()
    Book._drop_table()


def teardown_module(module):
    UserReview._drop_table()
    Book._drop_table()


def test_user_user_cf_simple():
    # Create simple dataset
    # User A: rates b1=5, b2=3
    # User B: rates b1=5, b2=2, b3=4
    # User C: rates b1=1, b3=5
    a1 = UserReview(id="r1", user_id="A", book_id="b1", rating=5.0)
    a1.post()
    a2 = UserReview(id="r2", user_id="A", book_id="b2", rating=3.0)
    a2.post()

    b1 = UserReview(id="r3", user_id="B", book_id="b1", rating=5.0)
    b1.post()
    b2 = UserReview(id="r4", user_id="B", book_id="b2", rating=2.0)
    b2.post()
    b3 = UserReview(id="r5", user_id="B", book_id="b3", rating=4.0)
    b3.post()

    c1 = UserReview(id="r6", user_id="C", book_id="b1", rating=1.0)
    c1.post()
    c2 = UserReview(id="r7", user_id="C", book_id="b3", rating=5.0)
    c2.post()

    recs = recommend_for_user("A", k_neighbors=2, n_recs=5)
    # Expect b3 to be recommended for A (B and C neighbor info favors b3)
    assert len(recs) > 0
    top_book, score = recs[0]
    assert top_book == "b3"
