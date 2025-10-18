import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.append(".")

from sqlalchemy import delete, distinct, func, insert, select

from server.backend.postgres import PostgresSessionManager
from server.models import (
    GenreModel,
    MovieGenreModel,
    MovieModel,
    MoviesRawModel,
    RatingModel,
    RatingsRawModel,
    UserModel,
)

session_manager = PostgresSessionManager()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def cleanup():
    with session_manager.open_session() as session:
        # Delete in reverse dependency order
        session.execute(delete(RatingModel))  # No dependencies
        session.execute(delete(MovieGenreModel))  # No dependencies
        session.execute(delete(GenreModel))  # Now safe to delete
        session.execute(delete(MovieModel))  # Now safe to delete
        session.execute(delete(UserModel))  # Now safe to delete
        session.execute(delete(MoviesRawModel))  # Raw data
        session.execute(delete(RatingsRawModel))  # Raw data


def load_raw_data(data_dir: Path):
    """Load CSV data into raw tables"""
    logger.info("Loading raw data from CSV files...")

    # Load movies CSV
    movies_df = pd.read_csv(data_dir / "movies.csv")  # type: ignore
    logger.info(f"Loaded {len(movies_df)} movies")

    # Load ratings CSV
    ratings_df = pd.read_csv(data_dir / "ratings.csv")  # type: ignore
    logger.info(f"Loaded {len(ratings_df)} ratings")

    with session_manager.open_session() as session:
        # Clear existing raw data
        session.query(MoviesRawModel).delete()
        session.query(RatingsRawModel).delete()

        # Insert movies raw data
        movies_raw: list[MoviesRawModel] = []
        for _, row in movies_df.iterrows():
            row_dict = row.to_dict()  # type: ignore
            movies_raw.append(MoviesRawModel(**row_dict))
        session.add_all(movies_raw)

        # Insert ratings raw data
        ratings_raw: list[RatingsRawModel] = []
        for _, row in ratings_df.iterrows():
            row_dict = row.to_dict()  # type: ignore
            ratings_raw.append(RatingsRawModel(**row_dict))
        session.add_all(ratings_raw)
    logger.info("Raw data loaded successfully")


def populate_users():
    """Create and populate users table"""
    logger.info("Populating users table...")

    with session_manager.open_session() as session:
        # Clear existing users
        session.query(UserModel).delete()

        # Get unique user IDs from ratings_raw
        unique_user_ids = session.query(RatingsRawModel.userId).distinct().all()

        users = [UserModel(user_id=uid[0]) for uid in unique_user_ids]
        session.add_all(users)
    logger.info(f"Created {len(users)} users")


def populate_movies():
    """Create and populate movies table"""
    logger.info("Populating movies table...")

    with session_manager.open_session() as session:
        # Get movies from raw data
        movies_raw = session.query(MoviesRawModel).all()

        movies = [
            MovieModel(movie_id=movie.movieId, title=movie.title)
            for movie in movies_raw
        ]
        session.add_all(movies)
    logger.info(f"Created {len(movies)} movies")


def populate_genres():
    """Create and populate genres table using SQLAlchemy"""
    logger.info("Populating genres table...")

    with session_manager.open_session() as session:
        # Use SQLAlchemy func for PostgreSQL-specific functions
        # This replicates: UNNEST(string_to_array(genres, '|'))
        subquery = (
            select(
                func.unnest(func.string_to_array(MoviesRawModel.genres, "|")).label(
                    "genre"
                )
            )
            .where(MoviesRawModel.genres != "(no genres listed)")
            .subquery()
        )

        # Insert distinct trimmed genres
        insert_stmt = insert(GenreModel).from_select(
            ["genre_name"], select(distinct(func.trim(subquery.c.genre)))
        )

        session.execute(insert_stmt)
    logger.info("Created genres using SQLAlchemy func expressions")


def populate_movie_genres():
    """Create and populate movie_genres junction table"""
    logger.info("Populating movie_genres junction table...")

    with session_manager.open_session() as session:
        # Use SQLAlchemy func for PostgreSQL-specific functions
        # This replicates the SQL:
        # SELECT DISTINCT mr.movieId, g.genre_id
        # FROM movies_raw mr
        # CROSS JOIN LATERAL (SELECT UNNEST(string_to_array(mr.genres, '|')) AS genre_name) AS split
        # JOIN genres g ON TRIM(split.genre_name) = g.genre_name
        # WHERE mr.genres != '(no genres listed)'

        split_subquery = (
            select(
                MoviesRawModel.movieId,
                func.unnest(func.string_to_array(MoviesRawModel.genres, "|")).label(
                    "genre_name"
                ),
            )
            .where(MoviesRawModel.genres != "(no genres listed)")
            .subquery()
        )

        # Join with genres table to get genre_ids
        insert_stmt = insert(MovieGenreModel).from_select(
            ["movie_id", "genre_id"],
            select(distinct(split_subquery.c.movieId), GenreModel.genre_id).select_from(
                split_subquery.join(
                    GenreModel,
                    func.trim(split_subquery.c.genre_name) == GenreModel.genre_name,
                )
            ),
        )

        session.execute(insert_stmt)
    logger.info("Created movie-genre relationships using SQLAlchemy func expressions")


def populate_ratings():
    """Create and populate ratings table"""
    logger.info("Populating ratings table...")

    with session_manager.open_session() as session:
        # Use SQLAlchemy func to convert Unix timestamp to datetime
        # This replicates: SELECT userId, movieId, rating, to_timestamp(timestamp) FROM ratings_raw
        insert_stmt = insert(RatingModel).from_select(
            ["user_id", "movie_id", "rating", "timestamp"],
            select(
                RatingsRawModel.userId,
                RatingsRawModel.movieId,
                RatingsRawModel.rating,
                func.to_timestamp(RatingsRawModel.timestamp),
            ),
        )

        session.execute(insert_stmt)
    logger.info("Created ratings using SQLAlchemy func expressions")


def main(data_directory: Path):
    cleanup()
    load_raw_data(data_directory)
    populate_users()
    populate_movies()
    populate_genres()
    populate_movie_genres()
    populate_ratings()


if __name__ == "__main__":
    data_directory = Path("data/small")
    main(data_directory)
