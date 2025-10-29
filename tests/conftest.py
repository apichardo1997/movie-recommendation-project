"""
Pytest configuration and fixtures for testing
BONUS Features #1 & #2: Service and router-level tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from server.app import app
from server.models.base import BaseSQLModel as Base
from server.models.movies import MovieModel
from server.models.genres import GenreModel
from server.models.user import UserModel
from server.models.ratings import RatingModel


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_client():
    """Create a test client for FastAPI"""
    return TestClient(app)


@pytest.fixture(scope="function")
def sample_movies(test_session):
    """Create sample movies for testing"""
    # Create genres
    action = GenreModel(name="Action")
    comedy = GenreModel(name="Comedy")
    drama = GenreModel(name="Drama")

    test_session.add_all([action, comedy, drama])
    test_session.commit()

    # Create movies
    movie1 = MovieModel(id=1, title="Test Action Movie", release_year=2020)
    movie1.genres.append(action)

    movie2 = MovieModel(id=2, title="Test Comedy Movie", release_year=2021)
    movie2.genres.append(comedy)

    movie3 = MovieModel(id=3, title="Test Drama Movie", release_year=2022)
    movie3.genres.append(drama)

    test_session.add_all([movie1, movie2, movie3])
    test_session.commit()

    return [movie1, movie2, movie3]


@pytest.fixture(scope="function")
def sample_users(test_session):
    """Create sample users for testing"""
    user1 = UserModel(user_id=1)
    user2 = UserModel(user_id=2)
    user3 = UserModel(user_id=3)

    test_session.add_all([user1, user2, user3])
    test_session.commit()

    return [user1, user2, user3]


@pytest.fixture(scope="function")
def sample_ratings(test_session, sample_users, sample_movies):
    """Create sample ratings for testing"""
    from datetime import datetime

    ratings = [
        RatingModel(user_id=1, movie_id=1, rating=4.5, timestamp=datetime.now()),
        RatingModel(user_id=1, movie_id=2, rating=3.0, timestamp=datetime.now()),
        RatingModel(user_id=2, movie_id=1, rating=5.0, timestamp=datetime.now()),
        RatingModel(user_id=2, movie_id=3, rating=4.0, timestamp=datetime.now()),
        RatingModel(user_id=3, movie_id=2, rating=2.5, timestamp=datetime.now()),
    ]

    test_session.add_all(ratings)
    test_session.commit()

    return ratings
