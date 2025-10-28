from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from server.backend.postgres import PostgresSessionManager
from server.schemas.rating import RatingCreate, RatingResponse
from server.services.rating_service import create_rating
from server.utils.errors import bad_request_error

router = APIRouter(prefix="/api/rest/v1", tags=["ratings"])

session_manager = PostgresSessionManager()


def get_db():
    """Dependency to get a database session."""
    with session_manager.open_session() as session:
        yield session


@router.post("/ratings", response_model=RatingResponse)
def add_rating(
    rating_data: RatingCreate,
    response: Response,
    session: Session = Depends(get_db)
):
    """
    Create or update a movie rating.

    - **user_id**: ID of the user creating the rating
    - **movie_id**: ID of the movie being rated
    - **rating**: Rating value (0.5 to 5.0)

    If the user has already rated this movie, updates the existing rating.
    Otherwise, creates a new rating.

    Returns:
    - 201 Created: New rating was created
    - 200 OK: Existing rating was updated

    Raises 400 error if user/movie not found.
    """
    try:
        rating_obj, was_created = create_rating(
            session=session,
            user_id=rating_data.user_id,
            movie_id=rating_data.movie_id,
            rating=rating_data.rating
        )

        response.status_code = 201 if was_created else 200

        return RatingResponse(
            rating_id=rating_obj.rating_id,
            user_id=rating_obj.user_id,
            movie_id=rating_obj.movie_id,
            rating=rating_obj.rating,
            timestamp=rating_obj.timestamp
        )

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            if "user" in error_msg.lower():
                raise bad_request_error("USER_NOT_FOUND", error_msg)
            elif "movie" in error_msg.lower():
                raise bad_request_error("MOVIE_NOT_FOUND", error_msg)
        elif "already rated" in error_msg.lower():
            raise bad_request_error("DUPLICATE_RATING", error_msg)
        else:
            raise bad_request_error("INVALID_REQUEST", error_msg)
