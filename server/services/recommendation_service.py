import pickle
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.models.movies import MovieModel
from server.models.ratings import RatingModel
from server.models.user import UserModel


# Directory to store models (simulating a data lake)
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

# In-memory training status tracker
# In production, this would be in Redis or a database
training_status = {
    "status": "idle",  # idle, training, completed, failed
    "started_at": None,
    "completed_at": None,
    "model_version": None,
    "total_ratings": None,
    "error": None,
}


def train_recommendation_model(session: Session) -> dict:
    """
    Train a recommendation model using Non-Negative Matrix Factorization.

    Fetches all ratings from the database, creates a user-item matrix,
    trains an NMF model, and saves it with versioning.

    Updates global training_status throughout the process.

    Returns dict with model version and training info.
    """
    global training_status

    try:
        # Update status to training
        training_status["status"] = "training"
        training_status["started_at"] = datetime.now().isoformat()
        training_status["completed_at"] = None
        training_status["error"] = None

        # Fetch all ratings directly into DataFrame (much faster than ORM)
        query = session.query(
            RatingModel.user_id,
            RatingModel.movie_id,
            RatingModel.rating
        )
        df = pd.read_sql(query.statement, session.bind)

        if len(df) == 0:
            raise ValueError("No ratings available to train the model")

        total_ratings = len(df)

        # Create user-item matrix
        user_item_matrix = df.pivot_table(
            index="user_id", columns="movie_id", values="rating", fill_value=0
        )

        # Train NMF model
        n_components = min(20, min(user_item_matrix.shape) - 1)  # Adaptive components
        model = NMF(n_components=n_components, init="random", random_state=42, max_iter=200)
        user_features = model.fit_transform(user_item_matrix)
        item_features = model.components_

        # Create model version (timestamp-based)
        version = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save model and metadata
        model_data = {
            "version": version,
            "model": model,
            "user_features": user_features,
            "item_features": item_features,
            "user_ids": user_item_matrix.index.tolist(),
            "movie_ids": user_item_matrix.columns.tolist(),
            "trained_at": datetime.now().isoformat(),
            "total_ratings": total_ratings,
        }

        model_path = MODELS_DIR / f"recommendation_model_{version}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model_data, f)

        # Also save as "latest" for easy access
        latest_path = MODELS_DIR / "recommendation_model_latest.pkl"
        with open(latest_path, "wb") as f:
            pickle.dump(model_data, f)

        # Update status to completed
        training_status["status"] = "completed"
        training_status["completed_at"] = datetime.now().isoformat()
        training_status["model_version"] = version
        training_status["total_ratings"] = total_ratings

        return {
            "model_version": version,
            "total_ratings": total_ratings,
            "message": "Model trained successfully",
        }

    except Exception as e:
        # Update status to failed
        training_status["status"] = "failed"
        training_status["completed_at"] = datetime.now().isoformat()
        training_status["error"] = str(e)
        raise


def get_training_status() -> dict:
    """Get the current status of model training."""
    return training_status.copy()


def get_recommendations_for_user(
    session: Session, user_id: int, n: int = 10
) -> dict:
    """
    Get movie recommendations for a specific user.

    Uses the latest trained model to predict ratings and returns
    top N movies with highest predicted scores.

    Returns dict with movie_ids and probabilities.
    Raises ValueError if user not found or model not trained.
    """
    # Check if user exists
    user = session.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    # Load latest model
    latest_path = MODELS_DIR / "recommendation_model_latest.pkl"
    if not latest_path.exists():
        raise ValueError("No trained model found. Please train the model first.")

    with open(latest_path, "rb") as f:
        model_data = pickle.load(f)

    user_features = model_data["user_features"]
    item_features = model_data["item_features"]
    user_ids = model_data["user_ids"]
    movie_ids = model_data["movie_ids"]

    # Check if user was in training data
    if user_id not in user_ids:
        # For new users, return popular movies (most rated)
        popular_movies = (
            session.query(
                RatingModel.movie_id,
                func.count(RatingModel.rating_id).label("count")
            )
            .group_by(RatingModel.movie_id)
            .order_by(func.count(RatingModel.rating_id).desc())
            .limit(n)
            .all()
        )

        movie_ids_list = [m.movie_id for m in popular_movies]
        # Normalize counts to probabilities
        counts = [m.count for m in popular_movies]
        total = sum(counts)
        probabilities = [c / total for c in counts]

        return {"movie_ids": movie_ids_list, "probabilities": probabilities}

    # Get user index
    user_idx = user_ids.index(user_id)

    # Predict ratings for all movies
    user_vector = user_features[user_idx].reshape(1, -1)
    predictions = np.dot(user_vector, item_features).flatten()

    # Create movie_id to prediction mapping
    movie_predictions = list(zip(movie_ids, predictions))

    # Sort by prediction score (descending) and get top N
    movie_predictions.sort(key=lambda x: x[1], reverse=True)
    top_recommendations = movie_predictions[:n]

    # Extract movie_ids and normalize probabilities
    recommended_movie_ids = [int(movie_id) for movie_id, _ in top_recommendations]
    raw_scores = [float(score) for _, score in top_recommendations]

    # Normalize scores to probabilities (sum to 1)
    total_score = sum(raw_scores)
    if total_score > 0:
        probabilities = [score / total_score for score in raw_scores]
    else:
        probabilities = [1.0 / len(raw_scores)] * len(raw_scores)

    return {"movie_ids": recommended_movie_ids, "probabilities": probabilities}
