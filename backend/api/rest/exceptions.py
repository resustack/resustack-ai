"""API 예외 정의 및 핸들러."""

import logging
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ReviewValidationError(Exception):
    """리뷰 검증 오류."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)


class ReviewServiceError(Exception):
    """리뷰 서비스 오류."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)


async def review_validation_error_handler(
    request: Request,
    exc: ReviewValidationError,
) -> JSONResponse:
    """리뷰 검증 오류 핸들러."""
    logger.warning(
        f"리뷰 검증 오류: {exc.message}",
        extra={"context": exc.context},
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


async def review_service_error_handler(
    request: Request,
    exc: ReviewServiceError,
) -> JSONResponse:
    """리뷰 서비스 오류 핸들러."""
    logger.error(
        f"리뷰 서비스 오류: {exc.message}",
        extra={"context": exc.context},
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"AI 서비스 오류: {exc.message}"},
    )


async def value_error_handler(
    request: Request,
    exc: ValueError,
) -> JSONResponse:
    """ValueError 핸들러.

    RequestValidationError는 ValueError의 서브클래스이므로,
    FastAPI 기본 422 핸들러가 처리하도록 재발생시킵니다.
    """
    if isinstance(exc, RequestValidationError):
        raise exc
    logger.warning(f"검증 오류: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """일반 예외 핸들러."""
    logger.error(f"예상치 못한 오류: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"AI 서비스 오류: {str(exc)}"},
    )
