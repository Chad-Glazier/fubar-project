from typing import Dict, List, Tuple
import math

from db.models.UserReview import UserReview


def _build_user_item_map() -> Dict[str, Dict[str, float]]:
    """Return mapping user_id -> {book_id: rating} for all reviews."""
    users: Dict[str, Dict[str, float]] = {}
    for r in UserReview.get_all():
        users.setdefault(r.user_id, {})[r.book_id] = float(r.rating)
    return users


def _cosine(u: Dict[str, float], v: Dict[str, float]) -> float:
    common = set(u.keys()) & set(v.keys())
    if not common:
        return 0.0
    dot = sum(u[b] * v[b] for b in common)
    nu = math.sqrt(sum(val * val for val in u.values()))
    nv = math.sqrt(sum(val * val for val in v.values()))
    if nu == 0.0 or nv == 0.0:
        return 0.0
    return dot / (nu * nv)


def recommend_for_user(user_id: str, k_neighbors: int = 5, n_recs: int = 10) -> List[Tuple[str, float]]:
    """Return top-n (book_id, score) recommendations for user_id using user-user CF.

    Scores are weighted averages of neighbor ratings using cosine similarity.
    """
    users = _build_user_item_map()

    # Cold-start or unknown user fallback: recommend popular books by average rating
    if user_id not in users or len(users.get(user_id, {})) == 0:
        # compute average rating per book
        totals: Dict[str, float] = {}
        counts: Dict[str, int] = {}
        for uvec in users.values():
            for b, r in uvec.items():
                totals[b] = totals.get(b, 0.0) + r
                counts[b] = counts.get(b, 0) + 1
        avg_scores: Dict[str, float] = {}
        for b in totals:
            avg_scores[b] = totals[b] / counts[b]
        ranked = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:n_recs]

    target = users[user_id]

    # compute similarities
    sims: List[Tuple[str, float]] = []
    for other_id, vec in users.items():
        if other_id == user_id:
            continue
        s = _cosine(target, vec)
        if s > 0:
            sims.append((other_id, s))

    sims.sort(key=lambda x: x[1], reverse=True)
    neighbors = sims[:k_neighbors]

    # candidate books = all books in data minus those user already rated
    candidate_books = set()
    for uvec in users.values():
        candidate_books.update(uvec.keys())
    candidate_books.difference_update(set(target.keys()))

    scores: Dict[str, float] = {}
    for book in candidate_books:
        num = 0.0
        den = 0.0
        for nb_id, sim in neighbors:
            nb_rating = users[nb_id].get(book)
            if nb_rating is not None:
                num += sim * nb_rating
                den += abs(sim)
        if den > 0:
            scores[book] = num / den

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:n_recs]
