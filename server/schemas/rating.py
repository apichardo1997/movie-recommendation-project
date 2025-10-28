from datetime import datetime

from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    """Schema for creating a new rating."""

    user_id: int = Field(..., gt=0, description="User ID (must be positive)")
    movie_id: int = Field(..., gt=0, description="Movie ID (must be positive)")
    rating: float = Field(..., ge=0.5, le=5.0, description="Rating value (0.5 to 5.0)")


class RatingResponse(BaseModel):
    """Schema for rating response."""

    rating_id: int = Field(..., description="Unique rating ID")
    user_id: int = Field(..., description="User ID")
    movie_id: int = Field(..., description="Movie ID")
    rating: float = Field(..., ge=0.5, le=5.0, description="Rating value (0.5 to 5.0)")
    timestamp: datetime = Field(..., description="When the rating was created")
