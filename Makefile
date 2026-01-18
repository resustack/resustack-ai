.PHONY: dev start test lint format typecheck clean

# 개발 서버 실행 (auto-reload)
dev:
	uv run python -m backend.main dev

# 프로덕션 서버 실행 (멀티 워커)
start:
	uv run python -m backend.main prod

# 테스트 실행
test:
	uv run pytest

# 린트 검사
lint:
	uv run ruff check backend tests

# 코드 포매팅
format:
	uv run ruff format backend tests

# 타입 체크
typecheck:
	uv run mypy backend

# 전체 검사 (린트 + 타입 체크 + 테스트)
check: lint typecheck test

# 클린업
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
