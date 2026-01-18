from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.rest.exceptions import (
    ReviewServiceError,
    ReviewValidationError,
    generic_exception_handler,
    review_service_error_handler,
    review_validation_error_handler,
    value_error_handler,
)
from backend.api.rest.v1.routes.reviews import router as api_v1_reviews_router

app = FastAPI(
    title="Resustack AI Service",
    description="AI-powered resume review and JD matching service",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 예외 핸들러 등록
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
    return {"status": "healthy"}
