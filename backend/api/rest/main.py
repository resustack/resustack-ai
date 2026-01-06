"""FastAPI application for REST API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.rest.v1.routes import resumes as api_v1_resumes

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

app.include_router(api_v1_resumes.router, prefix="/api/v1/resumes")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - service status."""
    return {"status": "ok", "service": "resustack-ai-service"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
