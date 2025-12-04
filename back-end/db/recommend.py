from typing import Dict, List, Tuple, Iterable, Set
import math
from pathlib import Path
from threading import Lock

from db.models.UserReview import UserReview

_cached_users: Dict[str, Dict[str, float]] | None = None
_cached_mtime: float = -1.0
_cache_lock: Lock = Lock()


def _reviews_file_mtime() -> float:
    file_path = Path(UserReview.data_dir + f"/{UserReview.__name__}.csv")
    if file_path.exists():
        return file_path.stat().st_mtime
    return -1.0


def invalidate_recommendation_cache() -> None:
    """Helper for tests or maintenance to clear the in-memory cache."""
    global _cached_users, _cached_mtime
    with _cache_lock:
        _cached_users = None
        _cached_mtime = -1.0


def _build_user_item_map() -> Dict[str, Dict[str, float]]:
    """Return mapping user_id -> {book_id: rating} with simple file mtime caching."""
    global _cached_users, _cached_mtime
    current_mtime = _reviews_file_mtime()
    with _cache_lock:
        if _cached_users is not None and current_mtime == _cached_mtime:
            return _cached_users

        users: Dict[str, Dict[str, float]] = {}
        for r in UserReview.get_all():
            users.setdefault(r.user_id, {})[r.book_id] = float(r.rating)

        _cached_users = users
        _cached_mtime = current_mtime
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

def _global_rank(users: Dict[str, Dict[str, float]], exclude: Iterable[str] | None = None) -> List[Tuple[str, float]]:
    totals: Dict[str, float] = {}
    counts: Dict[str, int] = {}
    for uvec in users.values():
        for b, r in uvec.items():
            totals[b] = totals.get(b, 0.0) + r
            counts[b] = counts.get(b, 0) + 1

    ranked = sorted(
        ((book_id, totals[book_id] / counts[book_id]) for book_id in totals.keys()),
        key=lambda x: x[1],
        reverse=True,
    )

    if exclude:
        exclude_set = set(exclude)
        ranked = [item for item in ranked if item[0] not in exclude_set]
    return ranked


def recommend_for_user(user_id: str, k_neighbors: int = 5, n_recs: int = 10) -> List[Tuple[str, float]]:
    """Return top-n (book_id, score) recommendations for user_id using user-user CF.

    Scores are weighted averages of neighbor ratings using cosine similarity.
    """
    users = _build_user_item_map()

    # Cold-start or unknown user fallback: recommend popular books by average rating
    if user_id not in users or len(users.get(user_id, {})) == 0:
        return _global_rank(users)[:n_recs]

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

    # If there are no similar neighbors with positive similarity,
    # fall back to recommending by global average (cold-start style).
    if not neighbors:
        ranked = _global_rank(users, exclude=target.keys())
        return ranked[:n_recs]

    neighbor_vectors: List[Tuple[Dict[str, float], float]] = [
        (users[nb_id], sim) for nb_id, sim in neighbors
    ]
    candidate_books: Set[str] = set()
    for vec, _ in neighbor_vectors:
        candidate_books.update(vec.keys())
    candidate_books.difference_update(target.keys())

    # Score only books seen in neighborhood instead of scanning entire catalog.
    scores: Dict[str, float] = {}
    for book in candidate_books:
        num = 0.0
        den = 0.0
        for vec, sim in neighbor_vectors:
            nb_rating = vec.get(book)
            if nb_rating is not None:
                num += sim * nb_rating
                den += abs(sim)
        if den > 0:
            scores[book] = num / den

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:n_recs]
