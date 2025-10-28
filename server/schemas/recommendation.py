from pydantic import BaseModel, Field


class RecommendationResponse(BaseModel):
    """Schema for user movie recommendations response."""

    movie_ids: list[int] = Field(..., description="List of recommended movie IDs")
    probabilities: list[float] = Field(..., description="Probability scores for each recommendation")


class ModelTrainResponse(BaseModel):
    """Schema for model training response (async)."""

    message: str = Field(..., description="Status message")
    status: str = Field(..., description="Training status: training, completed, failed")


class TrainingStatusResponse(BaseModel):
    """Schema for training status check response."""

    status: str = Field(..., description="Current status: idle, training, completed, failed")
    started_at: str | None = Field(None, description="When training started")
    completed_at: str | None = Field(None, description="When training completed")
    model_version: str | None = Field(None, description="Version of trained model (if completed)")
    total_ratings: int | None = Field(None, description="Number of ratings used (if completed)")
    error: str | None = Field(None, description="Error message (if failed)")
