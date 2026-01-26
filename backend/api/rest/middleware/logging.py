import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app")


class LoggingMiddleware(BaseHTTPMiddleware):
    """HTTP 요청/응답을 로깅하는 미들웨어."""

    async def dispatch(self, request: Request, call_next):
        """요청을 처리하고 로깅합니다."""
        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            client_ip = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

            logger.error(
                "method=%s path=%s status=500 duration_ms=%.2f ip=%s ua=%s error=%s",
                request.method,
                request.url.path,
                process_time,
                client_ip,
                user_agent,
                str(e),
                exc_info=True,
            )
            raise

        process_time = (time.time() - start_time) * 1000
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.4f}s - "
            f"Path: {request.url.path}"
        )

        return response
