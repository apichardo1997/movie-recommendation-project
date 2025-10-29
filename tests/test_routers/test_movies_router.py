"""
BONUS #2: Router-level tests for movies router
Tests HTTP layer with mocked services
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from server.app import app


client = TestClient(app)


class TestMoviesRouter:
    """Test movies endpoints with mocked services"""

    @patch("server.routers.movies.get_movies")
    def test_list_movies_default(self, mock_get_movies):
        """Test GET /movies with default parameters"""
        # Mock service response
        mock_movie = MagicMock()
        mock_movie.id = 1
        mock_movie.title = "Test Movie"
        mock_movie.release_year = 2020
        mock_genre = MagicMock()
        mock_genre.name = "Action"
        mock_movie.genres = [mock_genre]

        mock_get_movies.return_value = ([mock_movie], 1)

        # Make request
        response = client.get("/api/rest/v1/movies")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "movies" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["limit"] == 10
        assert len(data["movies"]) == 1

        # Verify service was called correctly
        mock_get_movies.assert_called_once()

    @patch("server.routers.movies.get_movies")
    def test_list_movies_with_pagination(self, mock_get_movies):
        """Test GET /movies with custom pagination"""
        mock_get_movies.return_value = ([], 0)

        response = client.get("/api/rest/v1/movies?limit=20&page=2")

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 20
        assert data["page"] == 2

        # Verify service was called with correct parameters
        args, kwargs = mock_get_movies.call_args
        # Check that limit and page were passed (session is first arg)
        assert args[1] == 20  # limit
        assert args[2] == 2   # page

    @patch("server.routers.movies.get_movies")
    def test_list_movies_with_search(self, mock_get_movies):
        """Test GET /movies with search parameter"""
        mock_get_movies.return_value = ([], 0)

        response = client.get("/api/rest/v1/movies?search=action")

        assert response.status_code == 200

        # Verify search parameter was passed
        args, kwargs = mock_get_movies.call_args
        assert args[3] == "action"  # search parameter

    @patch("server.routers.movies.get_movies")
    def test_list_movies_with_sorting(self, mock_get_movies):
        """Test GET /movies with sort parameter"""
        mock_get_movies.return_value = ([], 0)

        response = client.get("/api/rest/v1/movies?sort_by=year_desc")

        assert response.status_code == 200

        # Verify sort parameter was passed
        args, kwargs = mock_get_movies.call_args
        assert args[4] == "year_desc"  # sort_by parameter

    def test_list_movies_invalid_limit(self):
        """Test GET /movies with invalid limit (too high)"""
        response = client.get("/api/rest/v1/movies?limit=500")

        assert response.status_code == 422  # Validation error

    def test_list_movies_invalid_page(self):
        """Test GET /movies with invalid page (negative)"""
        response = client.get("/api/rest/v1/movies?page=-1")

        assert response.status_code == 422  # Validation error

    @patch("server.routers.movies.get_movies")
    def test_list_movies_has_pagination_metadata(self, mock_get_movies):
        """Test response includes pagination metadata"""
        mock_get_movies.return_value = ([], 50)

        response = client.get("/api/rest/v1/movies?limit=10&page=3")

        assert response.status_code == 200
        data = response.json()
        assert "total_pages" in data
        assert "has_next" in data
        assert "has_previous" in data
        assert data["total_pages"] == 5  # 50 total / 10 per page
        assert data["has_previous"] is True  # page 3
        assert data["has_next"] is True  # page 3 of 5

    @patch("server.routers.movies.get_movie_avg_rating")
    def test_get_movie_rating_success(self, mock_get_rating):
        """Test GET /movies/{id}/avg-rating success"""
        mock_get_rating.return_value = {
            "movie_id": 1,
            "title": "Test Movie",
            "avg_rating": 4.5,
            "total_ratings": 10
        }

        response = client.get("/api/rest/v1/movies/1/avg-rating")

        assert response.status_code == 200
        data = response.json()
        assert data["movie_id"] == 1
        assert data["avg_rating"] == 4.5
        assert data["total_ratings"] == 10

    @patch("server.routers.movies.get_movie_avg_rating")
    def test_get_movie_rating_not_found(self, mock_get_rating):
        """Test GET /movies/{id}/avg-rating for non-existent movie"""
        mock_get_rating.return_value = None

        response = client.get("/api/rest/v1/movies/999/avg-rating")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "MOVIE_NOT_FOUND"

    def test_get_movie_rating_invalid_id(self):
        """Test GET /movies/{id}/avg-rating with invalid ID"""
        response = client.get("/api/rest/v1/movies/-1/avg-rating")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    @patch("server.routers.movies.get_movies")
    def test_list_movies_includes_genres(self, mock_get_movies):
        """Test that movie response includes genres"""
        mock_movie = MagicMock()
        mock_movie.id = 1
        mock_movie.title = "Test Movie"
        mock_movie.release_year = 2020
        mock_genre1 = MagicMock()
        mock_genre1.name = "Action"
        mock_genre2 = MagicMock()
        mock_genre2.name = "Adventure"
        mock_movie.genres = [mock_genre1, mock_genre2]

        mock_get_movies.return_value = ([mock_movie], 1)

        response = client.get("/api/rest/v1/movies")

        assert response.status_code == 200
        data = response.json()
        assert len(data["movies"][0]["genres"]) == 2
        assert "Action" in data["movies"][0]["genres"]
        assert "Adventure" in data["movies"][0]["genres"]
