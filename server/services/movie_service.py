from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from server.models.genres import GenreModel
from server.models.movies import MovieModel
from server.models.ratings import RatingModel


def _build_movie_search_query(session: Session, search: str | None = None):
    """Build base query for movies with optional search filter and eager loading."""
    query = session.query(MovieModel).options(joinedload(MovieModel.genres))

    if search:
        query = query.join(MovieModel.genres, isouter=True)
        query = query.filter(
            or_(
                MovieModel.title.ilike(f"%{search}%"),
                GenreModel.name.ilike(f"%{search}%")
            )
        )
        query = query.distinct()

    return query


def get_movies(
    session: Session,
    limit: int = 10,
    page: int = 1,
    search: str | None = None,
    sort_by: str | None = None
):
    """
    Get paginated list of movies from the database.

    Supports sorting by:
    - title_asc, title_desc: Sort by movie title
    - year_asc, year_desc: Sort by release year
    - id_asc, id_desc: Sort by movie ID

    Returns tuple of (movies, total_count).
    """
    offset = (page - 1) * limit

    base_query = _build_movie_search_query(session, search)

    # Apply sorting
    if sort_by == "title_asc":
        base_query = base_query.order_by(MovieModel.title.asc())
    elif sort_by == "title_desc":
        base_query = base_query.order_by(MovieModel.title.desc())
    elif sort_by == "year_asc":
        base_query = base_query.order_by(MovieModel.release_year.asc())
    elif sort_by == "year_desc":
        base_query = base_query.order_by(MovieModel.release_year.desc())
    elif sort_by == "id_asc":
        base_query = base_query.order_by(MovieModel.id.asc())
    elif sort_by == "id_desc":
        base_query = base_query.order_by(MovieModel.id.desc())
    else:
        # Default sorting by ID ascending
        base_query = base_query.order_by(MovieModel.id.asc())

    movies = base_query.offset(offset).limit(limit).all()

    total = base_query.count()

    return movies, total


def get_movie_avg_rating(session: Session, movie_id: int):
    """
    Get average rating for a specific movie.

    Returns dict with movie details and rating statistics, or None if movie not found.
    """
    movie = session.query(MovieModel).filter(MovieModel.id == movie_id).first()

    if not movie:
        return None

    result = session.query(
        func.avg(RatingModel.rating),
        func.count(RatingModel.rating)
    ).filter(RatingModel.movie_id == movie_id).first()

    avg_rating, total_ratings = result

    if avg_rating is None:
        avg_rating = 0.0

    return {
        "movie_id": movie.id,
        "title": movie.title,
        "avg_rating": float(avg_rating),
        "total_ratings": total_ratings
    }
