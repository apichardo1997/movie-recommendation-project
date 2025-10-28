from datetime import datetime

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Schema for error response details."""

    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the error occurred")


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: ErrorDetail = Field(..., description="Error details")
