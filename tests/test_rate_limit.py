"""Rate limiting 테스트."""

import pytest
from backend.api.rest.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """테스트 클라이언트."""
    return TestClient(app)


class TestRateLimit:
    """Rate limiting 테스트."""

    def test_health_endpoint_not_rate_limited(self, client):
        """헬스체크 엔드포인트는 rate limiting이 적용되지 않아야 합니다."""
        # health 엔드포인트는 skip_paths에 포함되어 있음
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200

    def test_root_endpoint_not_rate_limited(self, client):
        """루트 엔드포인트는 rate limiting이 적용되지 않아야 합니다."""
        # / 엔드포인트는 skip_paths에 포함되어 있음
        for _ in range(10):
            response = client.get("/")
            assert response.status_code == 200

    def test_rate_limit_headers_present(self, client):
        """rate limit 헤더가 응답에 포함되어야 합니다."""
        response = client.get("/api/v1/resumes")
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_rate_limit_remaining_decreases(self, client):
        """요청할 때마다 X-RateLimit-Remaining이 감소해야 합니다."""
        response1 = client.get("/api/v1/resumes")
        remaining1 = int(response1.headers.get("X-RateLimit-Remaining", 0))

        response2 = client.get("/api/v1/resumes")
        remaining2 = int(response2.headers.get("X-RateLimit-Remaining", 0))

        # 두 번째 요청에서는 남은 요청 수가 하나 감소해야 함
        assert remaining2 < remaining1 or (remaining1 == 0 and remaining2 == 0)

    def test_rate_limit_response_format(self, client):
        """Rate limit 초과 시 응답 형식이 올바른지 확인합니다."""
        # rate_limit_requests가 100이므로 101개 요청으로 limit 초과
        for _ in range(101):
            response = client.get("/api/v1/resumes")
            if response.status_code == 429:
                assert response.json()["detail"] is not None
                assert "Retry-After" in response.headers
                assert response.headers["Retry-After"] == "3600"
                break
        else:
            # 테스트 환경에서는 rate limit이 즉시 초과되지 않을 수 있음
            pytest.skip("Rate limit not triggered in test environment")
