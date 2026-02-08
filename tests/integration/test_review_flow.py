"""통합 테스트 - 리뷰 플로우."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from backend.api.rest.main import app
from backend.api.rest.v1.schemas.reviews import ReviewResponse, SectionReviewResponse
from backend.services import ReviewService, get_review_service
from fastapi.testclient import TestClient


def create_full_resume_json(profile_override: dict | None = None) -> dict:
    """전체 Resume JSON 데이터 생성 헬퍼."""
    now = datetime.now().isoformat()
    profile = {
        "name": "홍길동",
        "position": "백엔드 개발자",
        "introduction": "FastAPI 백엔드 개발 3년차입니다.",
        "email": "hong@example.com",
        "phone": "010-1234-5678",
    }
    if profile_override:
        profile.update(profile_override)

    return {
        "_id": "507f1f77bcf86cd799439011",
        "userId": 1,
        "title": "테스트 이력서",
        "templateId": 1,
        "status": "draft",
        "isPublic": False,
        "profile": profile,
        "sections": [],
        "skills": {},
        "createdAt": now,
        "updatedAt": now,
    }


@pytest.fixture
def mock_service() -> MagicMock:
    """Mock ReviewService."""
    return MagicMock(spec=ReviewService)


@pytest.fixture
def mock_client(mock_service: MagicMock) -> TestClient:
    """Mock이 적용된 TestClient."""
    app.dependency_overrides[get_review_service] = lambda: mock_service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestReviewIntegrationFlow:
    """리뷰 플로우 통합 테스트."""

    @pytest.mark.asyncio
    async def test_introduction_review_full_flow(
        self, mock_client: TestClient, mock_service: MagicMock
    ) -> None:
        """소개글 리뷰 전체 플로우 테스트."""
        resume_id = uuid4()

        # Mock 응답 설정
        mock_response = ReviewResponse(
            resume_id=resume_id,
            target_type="introduction",
            evaluation_summary="명확하고 구체적인 소개글입니다",
            strengths=["기술 스택 구체적", "경력 명시"],
            weaknesses=["차별화 포인트 부족"],
            improvement_suggestion="본인만의 강점을 추가하세요",
            improved_content="""
                저는 3년차 백엔드 개발자로,
                FastAPI를 활용한 마이크로서비스 아키텍처 설계 경험이 있습니다.
            """,
        )
        mock_service.review_introduction = AsyncMock(return_value=mock_response)

        # API 호출
        response = mock_client.post(
            f"/api/v1/resumes/{resume_id}/reviews/introduction",
            json=create_full_resume_json(),
        )

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data["targetType"] == "introduction"
        assert "명확하고 구체적" in data["evaluationSummary"]
        assert len(data["strengths"]) >= 1
        assert "improvedContent" in data
        mock_service.review_introduction.assert_called_once()

    @pytest.mark.asyncio
    async def test_block_review_with_validation_error(self, mock_client: TestClient) -> None:
        """블록 리뷰 - 잘못된 입력 검증."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id = uuid4()

        # 필수 필드 누락 - URL에서 section_id, block_id 제거됨
        response = mock_client.post(
            f"/api/v1/resumes/{resume_id}/reviews/project/block",
            json={
                "sectionId": str(section_id),
                "id": str(block_id),
                # subTitle 누락
                "period": "2023.01 - 2023.12",
                "content": "내용",
                "isVisible": True,
            },
        )

        assert response.status_code == 422
        error_detail = response.json()
        assert "detail" in error_detail

    @pytest.mark.asyncio
    async def test_section_review_multiple_blocks(
        self, mock_client: TestClient, mock_service: MagicMock
    ) -> None:
        """섹션 리뷰 - 여러 블록 처리."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id_1 = uuid4()
        block_id_2 = uuid4()
        block_id_3 = uuid4()

        from backend.api.rest.v1.schemas.reviews import BlockReviewResponse

        # Mock 응답 설정
        mock_response = SectionReviewResponse(
            resume_id=resume_id,
            section_id=section_id,
            target_type="project",
            overall_evaluation="다양한 프로젝트 경험",
            block_results=[
                BlockReviewResponse(
                    block_id=block_id_1,
                    evaluation_summary="프로젝트 1 평가",
                    strengths=["구체적"],
                    weaknesses=[],
                    improvement_suggestion="유지",
                ),
                BlockReviewResponse(
                    block_id=block_id_2,
                    evaluation_summary="프로젝트 2 평가",
                    strengths=["명확함"],
                    weaknesses=[],
                    improvement_suggestion="유지",
                ),
                BlockReviewResponse(
                    block_id=block_id_3,
                    evaluation_summary="프로젝트 3 평가",
                    strengths=["상세함"],
                    weaknesses=[],
                    improvement_suggestion="유지",
                ),
            ],
        )
        mock_service.review_section = AsyncMock(return_value=mock_response)

        response = mock_client.post(
            f"/api/v1/resumes/{resume_id}/reviews/project",
            json={
                "id": str(section_id),
                "type": "project",
                "title": "프로젝트",
                "orderIndex": 0,
                "blocks": [
                    {
                        "id": str(block_id_1),
                        "subTitle": "프로젝트 1",
                        "period": "2023.01 - 2023.12",
                        "content": "프로젝트 1 내용",
                        "isVisible": True,
                        "techStack": ["Python"],
                    },
                    {
                        "id": str(block_id_2),
                        "subTitle": "프로젝트 2",
                        "period": "2023.01 - 2023.12",
                        "content": "프로젝트 2 내용",
                        "isVisible": True,
                        "techStack": ["Python"],
                    },
                    {
                        "id": str(block_id_3),
                        "subTitle": "프로젝트 3",
                        "period": "2023.01 - 2023.12",
                        "content": "프로젝트 3 내용",
                        "isVisible": True,
                        "techStack": ["Python"],
                    },
                ],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["blockResults"]) == 3
        mock_service.review_section.assert_called_once()


class TestReviewErrorHandling:
    """리뷰 에러 처리 통합 테스트."""

    @pytest.mark.asyncio
    async def test_ai_service_failure(
        self, mock_client: TestClient, mock_service: MagicMock
    ) -> None:
        """AI 서비스 실패 시 에러 처리."""
        resume_id = uuid4()

        # 서비스 실패 시뮬레이션
        from backend.api.rest.exceptions import ReviewServiceError

        mock_service.review_introduction = AsyncMock(
            side_effect=ReviewServiceError("AI 서비스 오류")
        )

        response = mock_client.post(
            f"/api/v1/resumes/{resume_id}/reviews/introduction",
            json=create_full_resume_json(),
        )

        # 에러 응답 확인
        assert response.status_code == 500

    def test_invalid_resume_id_format(self, client: TestClient) -> None:
        """잘못된 resume_id 형식."""
        response = client.post(
            "/api/v1/resumes/invalid-uuid/reviews/introduction",
            json=create_full_resume_json(),
        )

        assert response.status_code == 422


class TestReviewDataFlow:
    """리뷰 데이터 흐름 테스트."""

    @pytest.mark.asyncio
    async def test_profile_data_preservation(
        self, mock_client: TestClient, mock_service: MagicMock
    ) -> None:
        """Profile 데이터가 리뷰 과정에서 보존되는지 확인."""
        resume_id = uuid4()

        profile_data = {
            "name": "홍길동",
            "position": "시니어 백엔드 개발자",
            "introduction": "10년차 백엔드 개발자입니다.",
            "email": "senior@example.com",
            "phone": "010-9999-8888",
            "github": "https://github.com/senior-dev",
        }

        mock_response = ReviewResponse(
            resume_id=resume_id,
            target_type="introduction",
            evaluation_summary="우수함",
            strengths=["경력"],
            weaknesses=[],
            improvement_suggestion="유지",
        )
        mock_service.review_introduction = AsyncMock(return_value=mock_response)

        response = mock_client.post(
            f"/api/v1/resumes/{resume_id}/reviews/introduction",
            json=create_full_resume_json(profile_override=profile_data),
        )

        assert response.status_code == 200

        # 서비스가 호출되었는지 검증
        mock_service.review_introduction.assert_called_once()

        # 전달된 request에 profile 데이터가 포함되어 있는지 확인
        call_args = mock_service.review_introduction.call_args
        request = call_args[0][1]  # 두 번째 위치 인수가 request
        assert request.profile.name == "홍길동"
        assert request.profile.position == "시니어 백엔드 개발자"

    @pytest.mark.asyncio
    async def test_tech_stack_in_block_review(
        self, mock_client: TestClient, mock_service: MagicMock
    ) -> None:
        """기술 스택이 블록 리뷰에 포함되는지 확인."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id = uuid4()

        tech_stack = ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"]

        mock_response = ReviewResponse(
            resume_id=resume_id,
            target_type="project_block",
            evaluation_summary="기술 스택 우수",
            strengths=["최신 기술 사용"],
            weaknesses=[],
            improvement_suggestion="유지",
            block_id=block_id,
        )
        mock_service.review_block = AsyncMock(return_value=mock_response)

        response = mock_client.post(
            f"/api/v1/resumes/{resume_id}/reviews/project/block",
            json={
                "sectionId": str(section_id),
                "id": str(block_id),
                "subTitle": "마이크로서비스 구축",
                "period": "2023.01 - 2023.12",
                "content": "FastAPI 기반 마이크로서비스 아키텍처 설계 및 구현",
                "isVisible": True,
                "techStack": tech_stack,
            },
        )

        assert response.status_code == 200
        # 서비스가 호출되었는지 확인
        mock_service.review_block.assert_called_once()

        # 전달된 request에 tech_stack이 포함되어 있는지 확인
        call_args = mock_service.review_block.call_args
        request = call_args[0][4]  # 다섯 번째 위치 인수가 request
        assert request.tech_stack == tech_stack
