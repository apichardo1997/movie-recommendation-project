from datetime import datetime
from fastapi import HTTPException


class APIError(HTTPException):
    """Custom exception with error code support."""

    def __init__(self, status_code: int, error_code: str, message: str):
        self.error_code = error_code
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": error_code,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )


# Common error factory functions
def not_found_error(resource: str, resource_id: int | str) -> APIError:
    """Create a 404 not found error."""
    return APIError(
        status_code=404,
        error_code=f"{resource.upper()}_NOT_FOUND",
        message=f"{resource.capitalize()} with ID {resource_id} not found"
    )


def bad_request_error(error_code: str, message: str) -> APIError:
    """Create a 400 bad request error."""
    return APIError(
        status_code=400,
        error_code=error_code,
        message=message
    )


def validation_error(field: str, message: str) -> APIError:
    """Create a 400 validation error."""
    return APIError(
        status_code=400,
        error_code="VALIDATION_ERROR",
        message=f"{field}: {message}"
    )
