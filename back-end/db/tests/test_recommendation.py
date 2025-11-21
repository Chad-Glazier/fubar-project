from db.models.UserReview import UserReview
from db.recommend import recommend_for_user

def test_user_user_cf_simple():
    # Create simple dataset
    # User A: rates b1=5, b2=3
    # User B: rates b1=5, b2=2, b3=4
    # User C: rates b1=1, b3=5
    reviews = [
        UserReview(id="r1", user_id="A", book_id="b1", rating=5.0),
        UserReview(id="r2", user_id="A", book_id="b2", rating=3.0),
        UserReview(id="r3", user_id="B", book_id="b1", rating=5.0),
        UserReview(id="r4", user_id="B", book_id="b2", rating=2.0),
        UserReview(id="r5", user_id="B", book_id="b3", rating=4.0),
        UserReview(id="r6", user_id="C", book_id="b1", rating=1.0),
        UserReview(id="r7", user_id="C", book_id="b3", rating=5.0)
	]
    for review in reviews: 
        review.put()

    recs = recommend_for_user("A", k_neighbors=2, n_recs=5)
    # Expect b3 to be recommended for A (B and C neighbor info favors b3)
    assert len(recs) > 0
    top_book, _ = recs[0]
    assert top_book == "b3"
    
    for review in reviews: 
        review.delete()
