from datetime import datetime

from sqlalchemy.orm import Session

from server.models.movies import MovieModel
from server.models.ratings import RatingModel
from server.models.user import UserModel


def create_rating(
    session: Session,
    user_id: int,
    movie_id: int,
    rating: float
) -> tuple[RatingModel, bool]:
    """
    Create or update a rating for a movie by a user.

    Validates that:
    - User exists
    - Movie exists

    If user has already rated this movie, updates the existing rating.
    Otherwise, creates a new rating.

    Returns tuple of (RatingModel, was_created: bool).
    was_created is True if new rating was created, False if existing rating was updated.
    Raises ValueError if user or movie not found.
    """
    user = session.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    movie = session.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not movie:
        raise ValueError(f"Movie with ID {movie_id} not found")

    existing_rating = session.query(RatingModel).filter(
        RatingModel.user_id == user_id,
        RatingModel.movie_id == movie_id
    ).first()

    if existing_rating:
        existing_rating.rating = rating
        existing_rating.timestamp = datetime.now()
        session.commit()
        session.refresh(existing_rating)
        return existing_rating, False

    new_rating = RatingModel(
        user_id=user_id,
        movie_id=movie_id,
        rating=rating,
        timestamp=datetime.now()
    )

    session.add(new_rating)
    session.commit()
    session.refresh(new_rating)

    return new_rating, True
