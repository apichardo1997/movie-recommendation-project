from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from server.backend.postgres import PostgresSessionManager
from server.schemas.recommendation import (
    RecommendationResponse,
    ModelTrainResponse,
    TrainingStatusResponse,
)
from server.services.recommendation_service import (
    train_recommendation_model,
    get_recommendations_for_user,
    get_training_status,
)
from server.utils.errors import bad_request_error, not_found_error

router = APIRouter(prefix="/api/rest/v1", tags=["recommendations"])

session_manager = PostgresSessionManager()


def get_db():
    """Dependency to get a database session."""
    with session_manager.open_session() as session:
        yield session


def train_model_background(session: Session):
    """Background task wrapper for model training."""
    try:
        train_recommendation_model(session)
    except Exception as e:
        # Error is already logged in training_status by the service
        print(f"Background training error: {e}")


@router.post("/recommendation-engine", response_model=ModelTrainResponse)
def train_model(background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    """
    Train the recommendation model based on current ratings data (async).

    Uses Non-Negative Matrix Factorization (NMF) to learn user and movie features.
    Training runs in the background to avoid blocking the API.

    Returns immediately with training status. Use GET /recommendation-engine/status
    to check training progress.

    **Bonus Feature:** Implements async workload using FastAPI background tasks.
    """
    current_status = get_training_status()

    if current_status["status"] == "training":
        return ModelTrainResponse(
            message="Model training already in progress",
            status="training",
        )

    # Start training in background
    background_tasks.add_task(train_model_background, session)

    return ModelTrainResponse(
        message="Model training started in background",
        status="training",
    )


@router.get("/recommendation-engine/status", response_model=TrainingStatusResponse)
def get_model_training_status():
    """
    Check the status of model training.

    Returns current training status including:
    - idle: No training has been started
    - training: Model is currently being trained
    - completed: Training finished successfully
    - failed: Training encountered an error

    Use this endpoint to poll training progress after calling POST /recommendation-engine.
    """
    status = get_training_status()
    return TrainingStatusResponse(**status)


@router.get("/user/{user_id}/recommended-movies", response_model=RecommendationResponse)
def get_user_recommendations(
    user_id: int,
    n: int = Query(default=10, ge=1, le=100, description="Number of recommendations (1-100)"),
    session: Session = Depends(get_db),
):
    """
    Get movie recommendations for a specific user.

    Uses the latest trained recommendation model to predict which movies
    the user is most likely to enjoy based on collaborative filtering.

    - **user_id**: ID of the user to get recommendations for
    - **n**: Number of movie recommendations to return (default: 10, max: 100)

    Returns list of movie IDs sorted by predicted preference (highest first)
    along with probability scores.
    """
    if user_id < 1:
        raise bad_request_error("INVALID_USER_ID", "User ID must be a positive integer")

    try:
        result = get_recommendations_for_user(session, user_id, n)
        return RecommendationResponse(
            movie_ids=result["movie_ids"], probabilities=result["probabilities"]
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise not_found_error("user", user_id)
        elif "no trained model" in error_msg.lower():
            raise bad_request_error(
                "MODEL_NOT_TRAINED",
                "No recommendation model available. Please train the model first using POST /recommendation-engine",
            )
        else:
            raise bad_request_error("RECOMMENDATION_ERROR", error_msg)
