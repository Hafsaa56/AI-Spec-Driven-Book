from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Callable
import logging
import traceback
from pydantic import BaseModel
from enum import Enum


class ErrorCode(str, Enum):
    """Enumeration of error codes for the API."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: dict
    success: bool = False


class APIError(Exception):
    """Base API exception."""
    def __init__(self, message: str, error_code: ErrorCode, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error exception."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, 422)


class NotFoundError(APIError):
    """Resource not found exception."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.RESOURCE_NOT_FOUND, 404)


class ServiceUnavailableError(APIError):
    """Service unavailable exception."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.SERVICE_UNAVAILABLE, 503)


def setup_error_handlers(app: FastAPI):
    """Setup global error handlers for the application."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        logging.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")

        error_response = ErrorResponse(
            error={
                "code": str(exc.status_code),
                "message": str(exc.detail),
                "type": "HTTP_ERROR"
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        logging.error(f"Validation Error: {exc}")

        errors = []
        for error in exc.errors():
            errors.append({
                "field": str(error.get("loc", [])),
                "message": error.get("msg", "Validation error"),
                "type": error.get("type", "validation_error")
            })

        error_response = ErrorResponse(
            error={
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "Validation failed",
                "details": errors,
                "type": "VALIDATION_ERROR"
            }
        )

        return JSONResponse(
            status_code=422,
            content=error_response.dict()
        )

    @app.exception_handler(APIError)
    async def api_exception_handler(request: Request, exc: APIError):
        """Handle custom API errors."""
        logging.error(f"API Error: {exc.error_code} - {exc.message}")

        error_response = ErrorResponse(
            error={
                "code": exc.error_code,
                "message": exc.message,
                "status_code": exc.status_code,
                "type": "API_ERROR"
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logging.error(f"General Exception: {exc}")
        logging.error(f"Traceback: {traceback.format_exc()}")

        error_response = ErrorResponse(
            error={
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "An internal server error occurred",
                "type": "INTERNAL_ERROR",
                "debug_info": {
                    "error_type": type(exc).__name__,
                    "error_message": str(exc)
                } if app.debug else None
            }
        )

        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )


def add_logging_middleware(app: FastAPI):
    """Add request/response logging middleware."""

    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable):
        """Log incoming requests and outgoing responses."""
        start_time = __import__('time').time()

        # Log request
        logging.info(f"Request: {request.method} {request.url}")

        try:
            response = await call_next(request)
        except Exception as e:
            # Log exceptions
            logging.error(f"Request failed: {request.method} {request.url} - {str(e)}")
            raise

        # Calculate duration
        duration = __import__('time').time() - start_time

        # Log response
        logging.info(f"Response: {response.status_code} - {duration:.3f}s")

        return response


def setup_middleware(app: FastAPI):
    """Setup all middleware for the application."""
    setup_error_handlers(app)
    add_logging_middleware(app)