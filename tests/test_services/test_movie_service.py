"""
BONUS #1: Service-level tests for movie_service
Tests business logic directly without HTTP layer
"""

import pytest
from server.services.movie_service import get_movies, get_movie_avg_rating


class TestGetMovies:
    """Test movie listing service"""

    def test_get_movies_default(self, test_session, sample_movies):
        """Test getting movies with default pagination"""
        movies, total = get_movies(test_session, limit=10, page=1)

        assert len(movies) == 3
        assert total == 3
        assert movies[0].title == "Test Action Movie"

    def test_get_movies_pagination(self, test_session, sample_movies):
        """Test pagination works correctly"""
        movies, total = get_movies(test_session, limit=2, page=1)

        assert len(movies) == 2
        assert total == 3

        movies_page2, total2 = get_movies(test_session, limit=2, page=2)
        assert len(movies_page2) == 1
        assert total2 == 3

    def test_get_movies_search_by_title(self, test_session, sample_movies):
        """Test search by movie title"""
        movies, total = get_movies(test_session, limit=10, page=1, search="Action")

        assert len(movies) == 1
        assert total == 1
        assert "Action" in movies[0].title

    def test_get_movies_search_by_genre(self, test_session, sample_movies):
        """Test search by genre name"""
        movies, total = get_movies(test_session, limit=10, page=1, search="Comedy")

        assert len(movies) == 1
        assert total == 1
        assert any(g.name == "Comedy" for g in movies[0].genres)

    def test_get_movies_sort_by_title_asc(self, test_session, sample_movies):
        """Test sorting by title ascending"""
        movies, total = get_movies(test_session, limit=10, page=1, sort_by="title_asc")

        assert len(movies) == 3
        assert movies[0].title == "Test Action Movie"
        assert movies[1].title == "Test Comedy Movie"
        assert movies[2].title == "Test Drama Movie"

    def test_get_movies_sort_by_year_desc(self, test_session, sample_movies):
        """Test sorting by year descending"""
        movies, total = get_movies(test_session, limit=10, page=1, sort_by="year_desc")

        assert len(movies) == 3
        assert movies[0].release_year == 2022
        assert movies[1].release_year == 2021
        assert movies[2].release_year == 2020

    def test_get_movies_empty_search(self, test_session, sample_movies):
        """Test search with no results"""
        movies, total = get_movies(test_session, limit=10, page=1, search="NonExistent")

        assert len(movies) == 0
        assert total == 0


class TestGetMovieRating:
    """Test movie rating retrieval service"""

    def test_get_movie_avg_rating_success(self, test_session, sample_movies, sample_ratings):
        """Test getting rating for a movie with ratings"""
        result = get_movie_avg_rating(test_session, movie_id=1)

        assert result["movie_id"] == 1
        assert result["title"] == "Test Action Movie"
        assert result["avg_rating"] == 4.75  # (4.5 + 5.0) / 2
        assert result["total_ratings"] == 2

    def test_get_movie_avg_rating_no_ratings(self, test_session, sample_movies):
        """Test getting rating for a movie with no ratings"""
        result = get_movie_avg_rating(test_session, movie_id=3)

        assert result["movie_id"] == 3
        assert result["title"] == "Test Drama Movie"
        assert result["avg_rating"] == 0.0
        assert result["total_ratings"] == 0

    def test_get_movie_avg_rating_not_found(self, test_session):
        """Test getting rating for non-existent movie"""
        result = get_movie_avg_rating(test_session, movie_id=999)
        assert result is None

    def test_get_movie_avg_rating_single_rating(self, test_session, sample_movies, sample_ratings):
        """Test movie with exactly one rating"""
        result = get_movie_avg_rating(test_session, movie_id=2)

        assert result["movie_id"] == 2
        assert result["avg_rating"] == 2.75  # (3.0 + 2.5) / 2
        assert result["total_ratings"] == 2
