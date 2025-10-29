"""
BONUS #2: Router-level tests for recommendations router
Tests HTTP layer with mocked services including async training
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from server.app import app


client = TestClient(app)


class TestRecommendationsRouter:
    """Test recommendations endpoints with mocked services"""

    @patch("server.routers.recommendations.get_training_status")
    @patch("server.routers.recommendations.BackgroundTasks.add_task")
    def test_train_model_starts_background_task(self, mock_add_task, mock_get_status):
        """Test POST /recommendation-engine starts training in background (BONUS #3)"""
        # Mock status to show no training in progress
        mock_get_status.return_value = {"status": "idle"}

        response = client.post("/api/rest/v1/recommendation-engine")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "training"
        assert "background" in data["message"].lower()

        # Verify background task was added
        mock_add_task.assert_called_once()

    @patch("server.routers.recommendations.get_training_status")
    def test_train_model_already_training(self, mock_get_status):
        """Test POST /recommendation-engine when training already in progress"""
        mock_get_status.return_value = {"status": "training"}

        response = client.post("/api/rest/v1/recommendation-engine")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "training"
        assert "already in progress" in data["message"].lower()

    @patch("server.routers.recommendations.get_training_status")
    def test_get_training_status_idle(self, mock_get_status):
        """Test GET /recommendation-engine/status when idle"""
        mock_get_status.return_value = {
            "status": "idle",
            "started_at": None,
            "completed_at": None,
            "model_version": None,
            "total_ratings": None,
            "error": None
        }

        response = client.get("/api/rest/v1/recommendation-engine/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "idle"

    @patch("server.routers.recommendations.get_training_status")
    def test_get_training_status_completed(self, mock_get_status):
        """Test GET /recommendation-engine/status when completed"""
        mock_get_status.return_value = {
            "status": "completed",
            "started_at": "2024-10-29T10:00:00",
            "completed_at": "2024-10-29T10:02:00",
            "model_version": "20241029_100000",
            "total_ratings": 100000,
            "error": None
        }

        response = client.get("/api/rest/v1/recommendation-engine/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["model_version"] == "20241029_100000"
        assert data["total_ratings"] == 100000

    @patch("server.routers.recommendations.get_training_status")
    def test_get_training_status_failed(self, mock_get_status):
        """Test GET /recommendation-engine/status when failed"""
        mock_get_status.return_value = {
            "status": "failed",
            "started_at": "2024-10-29T10:00:00",
            "completed_at": "2024-10-29T10:01:00",
            "model_version": None,
            "total_ratings": None,
            "error": "No ratings available"
        }

        response = client.get("/api/rest/v1/recommendation-engine/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error"] is not None

    @patch("server.routers.recommendations.get_recommendations_for_user")
    def test_get_recommendations_success(self, mock_get_recs):
        """Test GET /user/{id}/recommended-movies success"""
        mock_get_recs.return_value = {
            "movie_ids": [1, 5, 10, 20, 30],
            "probabilities": [0.3, 0.25, 0.2, 0.15, 0.1]
        }

        response = client.get("/api/rest/v1/user/1/recommended-movies?n=5")

        assert response.status_code == 200
        data = response.json()
        assert "movie_ids" in data
        assert "probabilities" in data
        assert len(data["movie_ids"]) == 5
        assert len(data["probabilities"]) == 5

        # Verify service was called with correct parameters
        mock_get_recs.assert_called_once()
        args, kwargs = mock_get_recs.call_args
        assert args[1] == 1  # user_id
        assert args[2] == 5  # n

    @patch("server.routers.recommendations.get_recommendations_for_user")
    def test_get_recommendations_default_n(self, mock_get_recs):
        """Test GET /user/{id}/recommended-movies with default n=10"""
        mock_get_recs.return_value = {
            "movie_ids": list(range(1, 11)),
            "probabilities": [0.1] * 10
        }

        response = client.get("/api/rest/v1/user/1/recommended-movies")

        assert response.status_code == 200
        data = response.json()
        assert len(data["movie_ids"]) == 10

        # Verify default n=10 was used
        args, kwargs = mock_get_recs.call_args
        assert args[2] == 10  # n default

    @patch("server.routers.recommendations.get_recommendations_for_user")
    def test_get_recommendations_user_not_found(self, mock_get_recs):
        """Test GET /user/{id}/recommended-movies for non-existent user"""
        mock_get_recs.side_effect = ValueError("User with ID 999 not found")

        response = client.get("/api/rest/v1/user/999/recommended-movies")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "USER_NOT_FOUND"

    @patch("server.routers.recommendations.get_recommendations_for_user")
    def test_get_recommendations_model_not_trained(self, mock_get_recs):
        """Test GET /user/{id}/recommended-movies when model not trained"""
        mock_get_recs.side_effect = ValueError("No trained model found. Please train the model first.")

        response = client.get("/api/rest/v1/user/1/recommended-movies")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "MODEL_NOT_TRAINED"

    def test_get_recommendations_invalid_user_id(self):
        """Test GET /user/{id}/recommended-movies with invalid user ID"""
        response = client.get("/api/rest/v1/user/-1/recommended-movies")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_get_recommendations_invalid_n(self):
        """Test GET /user/{id}/recommended-movies with invalid n parameter"""
        # n too low
        response = client.get("/api/rest/v1/user/1/recommended-movies?n=0")
        assert response.status_code == 422

        # n too high
        response = client.get("/api/rest/v1/user/1/recommended-movies?n=200")
        assert response.status_code == 422

    @patch("server.routers.recommendations.get_recommendations_for_user")
    def test_get_recommendations_custom_n_range(self, mock_get_recs):
        """Test various valid n values"""
        for n_value in [1, 5, 10, 50, 100]:
            mock_get_recs.return_value = {
                "movie_ids": list(range(1, n_value + 1)),
                "probabilities": [1.0 / n_value] * n_value
            }

            response = client.get(f"/api/rest/v1/user/1/recommended-movies?n={n_value}")

            assert response.status_code == 200
            data = response.json()
            assert len(data["movie_ids"]) == n_value

    @patch("server.routers.recommendations.get_recommendations_for_user")
    def test_get_recommendations_probabilities_included(self, mock_get_recs):
        """Test that recommendations include probability scores"""
        mock_get_recs.return_value = {
            "movie_ids": [1, 2, 3],
            "probabilities": [0.5, 0.3, 0.2]
        }

        response = client.get("/api/rest/v1/user/1/recommended-movies?n=3")

        assert response.status_code == 200
        data = response.json()
        assert data["probabilities"] == [0.5, 0.3, 0.2]
        assert len(data["probabilities"]) == len(data["movie_ids"])
