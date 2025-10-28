import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from server.routers import movies, ratings, recommendations
from server.utils.errors import APIError

app = FastAPI(
    title="Movie Recommendation API",
    description="API for recommending movies based on user preferences using MovieLens dataset.",
    version="1.0.0"
)


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Custom handler for APIError to return proper error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.middleware("http")
async def add_performance_headers(request: Request, call_next):
    """Middleware to add performance tracking headers to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    response.headers["X-Response-Time"] = f"{process_time:.2f}ms"
    return response


app.include_router(movies.router)
app.include_router(ratings.router)
app.include_router(recommendations.router)


@app.get("/")
def read_root():
    """Root endpoint to verify API is running."""
    return {"message": "Welcome to the Movie Recommendation API!"}


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}
