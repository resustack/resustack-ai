FROM python:3.12-slim as builder

WORKDIR /app

# install system packges
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PATH="/app/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1

# 프로젝트 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치 (프로덕션만)
RUN uv sync --frozen --no-dev

# 애플리케이션 스테이지
FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 설치 (런타임 필요사항)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 빌더 스테이지에서 설치된 의존성 복사
COPY --from=builder /app/.venv /app/.venv

# 애플리케이션 코드 복사
COPY backend ./backend

# 환경변수 설정
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app"

# 헬스체크
HEALTHCHECK --interval=60s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${APP_PORT:-8000}/health || exit 1

# 포트 노출
EXPOSE ${APP_PORT:-8000}

# 애플리케이션 실행
CMD ["python", "-m", "backend.main", "prod"]
