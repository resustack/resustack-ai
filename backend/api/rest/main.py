import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.rest.config import get_api_config
from backend.api.rest.exceptions import (
    ReviewServiceError,
    ReviewValidationError,
    generic_exception_handler,
    review_service_error_handler,
    review_validation_error_handler,
    value_error_handler,
)
from backend.api.rest.logging_config import setup_logging
from backend.api.rest.middleware import LoggingMiddleware, RateLimitMiddleware
from backend.api.rest.v1.routes.reviews import router as api_v1_reviews_router

app = FastAPI(
    title="Resustack AI Service",
    description="AI-powered resume review and JD matching service",
    version="0.1.0",
)

api_config = get_api_config()

# logging
setup_logging(level="DEBUG" if api_config.is_dev else "INFO")
logger = logging.getLogger(__name__)

app.add_middleware(LoggingMiddleware)

# Rate limiting
if api_config.rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=api_config.rate_limit_requests,
        skip_paths=api_config.rate_limit_skip_paths_list,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=api_config.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Exception handlers
app.add_exception_handler(ReviewValidationError, review_validation_error_handler)
app.add_exception_handler(ReviewServiceError, review_service_error_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(api_v1_reviews_router, prefix="/api/v1/resumes")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - service status."""
    return {"status": "ok", "service": "resustack-ai-service"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    logger.info("API Health Check")
    return {"status": "healthy"}
