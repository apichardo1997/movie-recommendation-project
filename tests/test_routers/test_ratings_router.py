"""
BONUS #2: Router-level tests for ratings router
Tests HTTP layer with mocked services
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from server.app import app


client = TestClient(app)


class TestRatingsRouter:
    """Test ratings endpoints with mocked services"""

    @patch("server.routers.ratings.create_rating")
    def test_create_rating_success(self, mock_create_rating):
        """Test POST /ratings creates new rating"""
        # Mock service response
        mock_rating = MagicMock()
        mock_rating.rating_id = 1
        mock_rating.user_id = 1
        mock_rating.movie_id = 2
        mock_rating.rating = 4.5
        mock_rating.timestamp = datetime.now()

        mock_create_rating.return_value = (mock_rating, True)  # Created

        # Make request
        response = client.post(
            "/api/rest/v1/ratings",
            json={"user_id": 1, "movie_id": 2, "rating": 4.5}
        )

        # Assertions
        assert response.status_code == 201  # Created
        data = response.json()
        assert data["rating_id"] == 1
        assert data["user_id"] == 1
        assert data["movie_id"] == 2
        assert data["rating"] == 4.5
        assert "timestamp" in data

        # Verify service was called
        mock_create_rating.assert_called_once()

    @patch("server.routers.ratings.create_rating")
    def test_update_rating_success(self, mock_create_rating):
        """Test POST /ratings updates existing rating"""
        # Mock service response for update
        mock_rating = MagicMock()
        mock_rating.rating_id = 1
        mock_rating.user_id = 1
        mock_rating.movie_id = 2
        mock_rating.rating = 5.0
        mock_rating.timestamp = datetime.now()

        mock_create_rating.return_value = (mock_rating, False)  # Updated, not created

        # Make request
        response = client.post(
            "/api/rest/v1/ratings",
            json={"user_id": 1, "movie_id": 2, "rating": 5.0}
        )

        # Assertions
        assert response.status_code == 200  # OK, not Created
        data = response.json()
        assert data["rating"] == 5.0

    @patch("server.routers.ratings.create_rating")
    def test_create_rating_user_not_found(self, mock_create_rating):
        """Test POST /ratings with non-existent user"""
        mock_create_rating.side_effect = ValueError("User with ID 999 not found")

        response = client.post(
            "/api/rest/v1/ratings",
            json={"user_id": 999, "movie_id": 1, "rating": 4.0}
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "USER_NOT_FOUND"

    @patch("server.routers.ratings.create_rating")
    def test_create_rating_movie_not_found(self, mock_create_rating):
        """Test POST /ratings with non-existent movie"""
        mock_create_rating.side_effect = ValueError("Movie with ID 999 not found")

        response = client.post(
            "/api/rest/v1/ratings",
            json={"user_id": 1, "movie_id": 999, "rating": 4.0}
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "MOVIE_NOT_FOUND"

    def test_create_rating_invalid_rating_too_high(self):
        """Test POST /ratings with rating > 5.0"""
        response = client.post(
            "/api/rest/v1/ratings",
            json={"user_id": 1, "movie_id": 1, "rating": 10.0}
        )

        assert response.status_code == 422  # Validation error

    def test_create_rating_invalid_rating_too_low(self):
        """Test POST /ratings with rating < 0.5"""
        response = client.post(
            "/api/rest/v1/ratings",
            json={"user_id": 1, "movie_id": 1, "rating": 0.0}
        )

        assert response.status_code == 422  # Validation error

    def test_create_rating_missing_fields(self):
        """Test POST /ratings with missing required fields"""
        response = client.post(
            "/api/rest/v1/ratings",
            json={"user_id": 1}  # Missing movie_id and rating
        )

        assert response.status_code == 422  # Validation error

    def test_create_rating_invalid_types(self):
        """Test POST /ratings with invalid field types"""
        response = client.post(
            "/api/rest/v1/ratings",
            json={"user_id": "not_a_number", "movie_id": 1, "rating": 4.0}
        )

        assert response.status_code == 422  # Validation error

    @patch("server.routers.ratings.create_rating")
    def test_create_rating_returns_timestamp(self, mock_create_rating):
        """Test that rating response includes timestamp"""
        mock_rating = MagicMock()
        mock_rating.rating_id = 1
        mock_rating.user_id = 1
        mock_rating.movie_id = 2
        mock_rating.rating = 4.5
        mock_rating.timestamp = datetime(2024, 10, 29, 12, 0, 0)

        mock_create_rating.return_value = (mock_rating, True)

        response = client.post(
            "/api/rest/v1/ratings",
            json={"user_id": 1, "movie_id": 2, "rating": 4.5}
        )

        assert response.status_code == 201
        data = response.json()
        assert "timestamp" in data
        assert data["timestamp"] is not None

    @patch("server.routers.ratings.create_rating")
    def test_create_rating_valid_range(self, mock_create_rating):
        """Test various valid ratings within range"""
        mock_rating = MagicMock()
        mock_rating.rating_id = 1
        mock_rating.user_id = 1
        mock_rating.movie_id = 1
        mock_rating.timestamp = datetime.now()

        for valid_rating in [0.5, 1.0, 2.5, 3.0, 4.5, 5.0]:
            mock_rating.rating = valid_rating
            mock_create_rating.return_value = (mock_rating, True)

            response = client.post(
                "/api/rest/v1/ratings",
                json={"user_id": 1, "movie_id": 1, "rating": valid_rating}
            )

            assert response.status_code == 201
            assert response.json()["rating"] == valid_rating
