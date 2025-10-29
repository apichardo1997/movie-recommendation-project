"""
BONUS #1: Service-level tests for recommendation_service
Tests ML model training and recommendation logic
"""

import pytest
import os
import shutil
from pathlib import Path
from server.services.recommendation_service import (
    train_recommendation_model,
    get_recommendations_for_user,
    get_training_status,
    MODELS_DIR
)


@pytest.fixture(scope="function")
def clean_models_dir():
    """Clean models directory before and after tests"""
    # Clean before
    if MODELS_DIR.exists():
        shutil.rmtree(MODELS_DIR)

    # Create fresh directory
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    yield

    # Clean after
    if MODELS_DIR.exists():
        shutil.rmtree(MODELS_DIR)


class TestTrainRecommendationModel:
    """Test ML model training service"""

    def test_train_model_success(self, test_session, sample_users, sample_movies, sample_ratings, clean_models_dir):
        """Test successful model training"""
        result = train_recommendation_model(test_session)

        assert "model_version" in result
        assert "total_ratings" in result
        assert "message" in result
        assert result["total_ratings"] == 5
        assert result["message"] == "Model trained successfully"

        # Check model file was created
        assert MODELS_DIR.exists()
        assert (MODELS_DIR / "recommendation_model_latest.pkl").exists()

    def test_train_model_creates_versioned_file(self, test_session, sample_users, sample_movies, sample_ratings, clean_models_dir):
        """Test that versioned model file is created"""
        result = train_recommendation_model(test_session)

        version = result["model_version"]
        versioned_file = MODELS_DIR / f"recommendation_model_{version}.pkl"

        assert versioned_file.exists()

    def test_train_model_no_ratings(self, test_session, sample_users, sample_movies, clean_models_dir):
        """Test training fails gracefully with no ratings"""
        with pytest.raises(ValueError, match="No ratings available to train the model"):
            train_recommendation_model(test_session)

    def test_train_model_updates_status(self, test_session, sample_users, sample_movies, sample_ratings, clean_models_dir):
        """Test that training updates global status"""
        train_recommendation_model(test_session)

        status = get_training_status()
        assert status["status"] == "completed"
        assert status["model_version"] is not None
        assert status["total_ratings"] == 5
        assert status["completed_at"] is not None

    def test_train_model_multiple_times(self, test_session, sample_users, sample_movies, sample_ratings, clean_models_dir):
        """Test training multiple times creates different versions"""
        result1 = train_recommendation_model(test_session)
        version1 = result1["model_version"]

        import time
        time.sleep(1)  # Ensure different timestamp

        result2 = train_recommendation_model(test_session)
        version2 = result2["model_version"]

        assert version1 != version2  # Different versions
        assert (MODELS_DIR / f"recommendation_model_{version1}.pkl").exists()
        assert (MODELS_DIR / f"recommendation_model_{version2}.pkl").exists()


class TestGetRecommendationsForUser:
    """Test recommendation retrieval service"""

    def test_get_recommendations_existing_user(self, test_session, sample_users, sample_movies, sample_ratings, clean_models_dir):
        """Test getting recommendations for user in training data"""
        # Train model first
        train_recommendation_model(test_session)

        # Get recommendations
        result = get_recommendations_for_user(test_session, user_id=1, n=2)

        assert "movie_ids" in result
        assert "probabilities" in result
        assert len(result["movie_ids"]) == 2
        assert len(result["probabilities"]) == 2
        assert all(isinstance(mid, int) for mid in result["movie_ids"])
        assert all(isinstance(p, float) for p in result["probabilities"])

    def test_get_recommendations_new_user(self, test_session, sample_users, sample_movies, sample_ratings, clean_models_dir):
        """Test getting recommendations for new user (not in training data)"""
        # Add a new user not in ratings
        from server.models.user import UserModel
        new_user = UserModel(user_id=99)
        test_session.add(new_user)
        test_session.commit()

        # Train model
        train_recommendation_model(test_session)

        # Get recommendations - should return popular movies
        result = get_recommendations_for_user(test_session, user_id=99, n=3)

        assert len(result["movie_ids"]) <= 3  # May be less if not enough rated movies
        assert len(result["probabilities"]) == len(result["movie_ids"])

    def test_get_recommendations_user_not_found(self, test_session, clean_models_dir):
        """Test error when user doesn't exist"""
        with pytest.raises(ValueError, match="User with ID 999 not found"):
            get_recommendations_for_user(test_session, user_id=999, n=10)

    def test_get_recommendations_no_model(self, test_session, sample_users, clean_models_dir):
        """Test error when model hasn't been trained"""
        with pytest.raises(ValueError, match="No trained model found"):
            get_recommendations_for_user(test_session, user_id=1, n=10)

    def test_get_recommendations_custom_n(self, test_session, sample_users, sample_movies, sample_ratings, clean_models_dir):
        """Test custom number of recommendations"""
        train_recommendation_model(test_session)

        result = get_recommendations_for_user(test_session, user_id=1, n=1)

        assert len(result["movie_ids"]) == 1
        assert len(result["probabilities"]) == 1

    def test_recommendations_probabilities_sum_to_one(self, test_session, sample_users, sample_movies, sample_ratings, clean_models_dir):
        """Test that probabilities are normalized (sum to 1)"""
        train_recommendation_model(test_session)

        result = get_recommendations_for_user(test_session, user_id=1, n=3)

        prob_sum = sum(result["probabilities"])
        assert abs(prob_sum - 1.0) < 0.01  # Allow small floating point error

    def test_recommendations_sorted_descending(self, test_session, sample_users, sample_movies, sample_ratings, clean_models_dir):
        """Test that recommendations are sorted by probability descending"""
        train_recommendation_model(test_session)

        result = get_recommendations_for_user(test_session, user_id=1, n=3)

        probs = result["probabilities"]
        for i in range(len(probs) - 1):
            assert probs[i] >= probs[i + 1]


class TestGetTrainingStatus:
    """Test training status retrieval"""

    def test_get_status_idle(self, clean_models_dir):
        """Test status when no training has occurred"""
        from server.services.recommendation_service import training_status
        # Reset to idle state
        training_status["status"] = "idle"
        training_status["started_at"] = None
        training_status["completed_at"] = None
        training_status["model_version"] = None
        training_status["total_ratings"] = None
        training_status["error"] = None

        status = get_training_status()

        assert status["status"] == "idle"
        assert status["model_version"] is None
        assert status["total_ratings"] is None

    def test_get_status_returns_copy(self):
        """Test that status returns a copy, not reference"""
        status1 = get_training_status()
        status2 = get_training_status()

        assert status1 is not status2  # Different objects
        assert status1 == status2  # Same content
