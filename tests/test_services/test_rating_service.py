"""
BONUS #1: Service-level tests for rating_service
Tests rating creation and update logic
"""

import pytest
from datetime import datetime
from server.services.rating_service import create_rating


class TestCreateRating:
    """Test rating creation service"""

    def test_create_new_rating(self, test_session, sample_users, sample_movies):
        """Test creating a new rating"""
        rating, was_created = create_rating(
            test_session, user_id=1, movie_id=1, rating=4.5
        )

        assert was_created is True
        assert rating.user_id == 1
        assert rating.movie_id == 1
        assert rating.rating == 4.5
        assert rating.rating_id is not None
        assert isinstance(rating.timestamp, datetime)

    def test_update_existing_rating(self, test_session, sample_users, sample_movies, sample_ratings):
        """Test updating an existing rating (update-not-reject pattern)"""
        # User 1 already rated movie 1 as 4.5
        original_rating_id = sample_ratings[0].rating_id

        # Update to 5.0
        rating, was_created = create_rating(
            test_session, user_id=1, movie_id=1, rating=5.0
        )

        assert was_created is False  # Should be update, not create
        assert rating.rating_id == original_rating_id  # Same ID
        assert rating.rating == 5.0  # Updated value
        assert rating.user_id == 1
        assert rating.movie_id == 1

    def test_create_rating_user_not_found(self, test_session, sample_movies):
        """Test creating rating for non-existent user"""
        with pytest.raises(ValueError, match="User with ID 999 not found"):
            create_rating(test_session, user_id=999, movie_id=1, rating=4.0)

    def test_create_rating_movie_not_found(self, test_session, sample_users):
        """Test creating rating for non-existent movie"""
        with pytest.raises(ValueError, match="Movie with ID 999 not found"):
            create_rating(test_session, user_id=1, movie_id=999, rating=4.0)

    def test_create_rating_min_value(self, test_session, sample_users, sample_movies):
        """Test creating rating with minimum value (0.5)"""
        rating, was_created = create_rating(
            test_session, user_id=1, movie_id=1, rating=0.5
        )

        assert was_created is True
        assert rating.rating == 0.5

    def test_create_rating_max_value(self, test_session, sample_users, sample_movies):
        """Test creating rating with maximum value (5.0)"""
        rating, was_created = create_rating(
            test_session, user_id=1, movie_id=1, rating=5.0
        )

        assert was_created is True
        assert rating.rating == 5.0

    def test_multiple_users_rate_same_movie(self, test_session, sample_users, sample_movies):
        """Test multiple users can rate the same movie"""
        rating1, created1 = create_rating(test_session, user_id=1, movie_id=1, rating=4.0)
        rating2, created2 = create_rating(test_session, user_id=2, movie_id=1, rating=5.0)
        rating3, created3 = create_rating(test_session, user_id=3, movie_id=1, rating=3.0)

        assert created1 is True
        assert created2 is True
        assert created3 is True
        assert rating1.rating_id != rating2.rating_id != rating3.rating_id

    def test_user_rates_multiple_movies(self, test_session, sample_users, sample_movies):
        """Test user can rate multiple movies"""
        rating1, created1 = create_rating(test_session, user_id=1, movie_id=1, rating=4.0)
        rating2, created2 = create_rating(test_session, user_id=1, movie_id=2, rating=5.0)
        rating3, created3 = create_rating(test_session, user_id=1, movie_id=3, rating=3.5)

        assert created1 is True
        assert created2 is True
        assert created3 is True
        assert rating1.movie_id != rating2.movie_id != rating3.movie_id
