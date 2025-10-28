import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from server.backend.postgres import PostgresSessionManager
from server.schemas.movie import MovieResponse, MovieListResponse, MovieAverageRatingResponse
from server.services.movie_service import get_movies, get_movie_avg_rating
from server.utils.errors import not_found_error, validation_error

router = APIRouter(prefix="/api/rest/v1", tags=["movies"]) #

session_manager = PostgresSessionManager()


def get_db():
    """Dependency to get a database session."""
    with session_manager.open_session() as session:
        yield session


@router.get("/movies", response_model=MovieListResponse)
def list_movies(
    limit: int = Query(default=10, ge=1, le=100, description="Number of movies per page (1-100)"),
    page: int = Query(default=1, ge=1, description="Page number (must be >= 1)"),
    search: str | None = Query(default=None, max_length=100, description="Search term for title or genre"),
    sort_by: str | None = Query(
        default=None,
        description="Sort by: title_asc, title_desc, year_asc, year_desc, id_asc, id_desc"
    ),
    session: Session = Depends(get_db),
):

    """
    List movies with pagination, search, and sorting.

    - **limit**: Number of movies per page (1-100)
    - **page**: Page number (starts at 1)
    - **search**: Optional search term to filter by title or genre
    - **sort_by**: Optional sorting (title_asc, title_desc, year_asc, year_desc, id_asc, id_desc)
    """
    movies, total = get_movies(session, limit, page, search, sort_by)

    movie_responses = [
        MovieResponse(
            id=m.id,
            title=m.title,
            release_year=m.release_year,
            genres=[g.name for g in m.genres]
        )
        for m in movies
    ]

    total_pages = math.ceil(total / limit) if total > 0 else 0

    return MovieListResponse(
        movies=movie_responses,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )


@router.get("/movies/{movie_id}/avg-rating", response_model=MovieAverageRatingResponse)
def get_movie_average_rating(
    movie_id: int,
    session: Session = Depends(get_db)
):
    """
    Get average rating for a specific movie.

    Returns the movie's average rating and total number of ratings.
    """
    if movie_id < 1:
        raise validation_error("movie_id", "Must be a positive integer")

    result = get_movie_avg_rating(session, movie_id)

    if result is None:
        raise not_found_error("movie", movie_id)

    return MovieAverageRatingResponse(
        movie_id=result["movie_id"],
        title=result["title"],
        avg_rating=result["avg_rating"],
        total_ratings=result["total_ratings"]
    )