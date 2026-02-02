import logging
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("app")


class RateLimitStore:
    """메모리 기반 rate limit 저장소."""

    def __init__(self):
        # {key: [(timestamp, count), ...]}
        self.requests: dict[str, list[tuple[datetime, int]]] = defaultdict(list)

    def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 3600,
    ) -> bool:
        """요청이 허용되는지 확인합니다.

        Args:
            key: Rate limit 키 (IP, user_id 등)
            max_requests: 시간 윈도우 내 최대 요청 수
            window_seconds: 시간 윈도우 (초 단위, 기본값 1시간)

        Returns:
            True if allowed, False otherwise
        """
        now = datetime.now(UTC)
        cutoff_time = now - timedelta(seconds=window_seconds)

        # 오래된 항목 제거
        self.requests[key] = [
            (timestamp, count)
            for timestamp, count in self.requests[key]
            if timestamp > cutoff_time
        ]

        # 현재 윈도우 내 요청 수 계산
        current_count = sum(count for _, count in self.requests[key])

        if current_count >= max_requests:
            return False

        # 새로운 요청 기록
        if self.requests[key] and self.requests[key][-1][0] == now:
            # 같은 초에 이미 요청이 있으면 카운트 증가
            timestamp, count = self.requests[key][-1]
            self.requests[key][-1] = (timestamp, count + 1)
        else:
            self.requests[key].append((now, 1))

        return True

    def get_remaining(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 3600,
    ) -> int:
        """남은 요청 수를 반환합니다."""
        now = datetime.now(UTC)
        cutoff_time = now - timedelta(seconds=window_seconds)

        current_count = sum(
            count
            for timestamp, count in self.requests[key]
            if timestamp > cutoff_time
        )

        return max(0, max_requests - current_count)


# 글로벌 rate limit 저장소
rate_limit_store = RateLimitStore()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting 미들웨어."""

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 3600,
        skip_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.skip_paths = skip_paths or []

    async def dispatch(self, request: Request, call_next: Callable):
        """Rate limiting을 적용합니다."""
        # 제외 경로 확인
        if request.url.path in self.skip_paths:
            return await call_next(request)

        # 클라이언트 IP 추출
        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{request.url.path}"

        # Rate limit 확인
        if not rate_limit_store.is_allowed(key, self.max_requests, self.window_seconds):
            remaining = rate_limit_store.get_remaining(
                key, self.max_requests, self.window_seconds
            )
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {request.url.path}"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. "
                    "Too many requests in a short time.",
                    "retry_after": self.window_seconds,
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(
                        int(
                            (
                                datetime.now(UTC)
                                + timedelta(seconds=self.window_seconds)
                            ).timestamp()
                        )
                    ),
                },
            )

        response = await call_next(request)

        # Rate limit 정보를 응답 헤더에 추가
        remaining = rate_limit_store.get_remaining(
            key, self.max_requests, self.window_seconds
        )
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(
                (
                    datetime.now(UTC)
                    + timedelta(seconds=self.window_seconds)
                ).timestamp()
            )
        )

        return response
