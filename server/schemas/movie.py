from pydantic import BaseModel, Field


class MovieResponse(BaseModel):
    """Schema for a single movie response."""

    id: int = Field(..., description="Movie ID")
    title: str = Field(..., description="Movie title")
    release_year: int | None = Field(None, description="Year the movie was released")
    genres: list[str] = Field(default_factory=list, description="List of genre names")


class MovieListResponse(BaseModel):
    """Schema for paginated movie list response."""

    movies: list[MovieResponse] = Field(..., description="List of movies")
    total: int = Field(..., ge=0, description="Total number of movies matching the query")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, le=100, description="Number of movies per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page available")
    has_previous: bool = Field(..., description="Whether there is a previous page available")


class MovieAverageRatingResponse(BaseModel):
    """Schema for movie average rating response."""

    movie_id: int = Field(..., description="Movie ID")
    title: str = Field(..., description="Movie title")
    avg_rating: float = Field(..., ge=0.0, le=5.0, description="Average rating (0.0-5.0)")
    total_ratings: int = Field(..., ge=0, description="Total number of ratings")
