"""리뷰 API 엔드포인트 테스트."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.api.rest.main import app
from backend.api.rest.v1.schemas.reviews import (
    BlockReviewResponse,
    ReviewResponse,
    SectionReviewResponse,
)
from backend.domain.resume.enums import SectionType
from backend.services.review import get_review_service
from backend.services.review.service import ReviewService


def create_full_resume_json(profile_override: dict | None = None) -> dict:
    """전체 Resume JSON 데이터 생성 헬퍼."""
    now = datetime.now().isoformat()
    profile = {
        "name": "홍길동",
        "position": "백엔드 개발자",
        "introduction": "FastAPI를 활용한 백엔드 개발 3년차입니다.",
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
def mock_review_service() -> MagicMock:
    """Mock ReviewService."""
    return MagicMock(spec=ReviewService)


@pytest.fixture
def client_with_mock_service(mock_review_service: MagicMock) -> TestClient:
    """Mock ReviewService를 주입한 TestClient."""
    app.dependency_overrides[get_review_service] = lambda: mock_review_service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestReviewIntroductionEndpoint:
    """소개글 리뷰 엔드포인트 테스트."""

    @pytest.mark.asyncio
    async def test_review_introduction_success(
        self, client_with_mock_service: TestClient, mock_review_service: MagicMock
    ) -> None:
        """소개글 리뷰 성공."""
        resume_id = uuid4()

        # Mock 응답 설정
        mock_response = ReviewResponse(
            resume_id=resume_id,
            target_type="introduction",
            evaluation_summary="전반적으로 우수합니다",
            strengths=["명확한 커리어 목표", "구체적인 기술 스택 언급"],
            weaknesses=["차별화 포인트 부족"],
            improvement_suggestion="본인만의 강점을 더 부각시키세요",
            improved_content="개선된 소개글 예시...",
        )
        mock_review_service.review_introduction = AsyncMock(return_value=mock_response)

        # API 호출
        response = client_with_mock_service.post(
            f"/api/v1/resumes/{resume_id}/reviews/introduction",
            json=create_full_resume_json(),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["targetType"] == "introduction"
        assert data["evaluationSummary"] == "전반적으로 우수합니다"
        assert len(data["strengths"]) == 2
        assert len(data["weaknesses"]) == 1

    def test_review_introduction_invalid_request(self, client: TestClient) -> None:
        """잘못된 요청 형식."""
        resume_id = uuid4()

        response = client.post(
            f"/api/v1/resumes/{resume_id}/reviews/introduction",
            json={},  # 필수 필드 누락
        )

        assert response.status_code == 422  # Validation Error


class TestReviewSkillsEndpoint:
    """스킬 리뷰 엔드포인트 테스트."""

    @pytest.mark.asyncio
    async def test_review_skills_success(
        self, client_with_mock_service: TestClient, mock_review_service: MagicMock
    ) -> None:
        """스킬 리뷰 성공."""
        resume_id = uuid4()

        mock_response = ReviewResponse(
            resume_id=resume_id,
            target_type="skill",
            evaluation_summary="균형잡힌 기술 스택입니다",
            strengths=["최신 트렌드 반영", "풀스택 역량"],
            weaknesses=["특정 분야 깊이 부족"],
            improvement_suggestion="전문성을 강화할 기술 선택이 필요합니다",
        )
        mock_review_service.review_skill = AsyncMock(return_value=mock_response)

        response = client_with_mock_service.post(
            f"/api/v1/resumes/{resume_id}/reviews/skills",
            json={
                "skills": {
                    "language": ["Python", "TypeScript"],
                    "framework": ["FastAPI", "React"],
                    "database": ["PostgreSQL", "Redis"],
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["targetType"] == "skill"
        assert "균형잡힌" in data["evaluationSummary"]


class TestReviewSectionEndpoint:
    """섹션 리뷰 엔드포인트 테스트."""

    @pytest.mark.asyncio
    async def test_review_section_success(
        self, client_with_mock_service: TestClient, mock_review_service: MagicMock
    ) -> None:
        """섹션 리뷰 성공."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id_1 = uuid4()
        block_id_2 = uuid4()

        # Mock 응답 설정
        mock_response = SectionReviewResponse(
            resume_id=resume_id,
            section_id=section_id,
            target_type="project",
            overall_evaluation="프로젝트 경험이 다양합니다",
            block_results=[
                BlockReviewResponse(
                    block_id=block_id_1,
                    evaluation_summary="기술적 깊이가 있습니다",
                    strengths=["구체적인 성과 지표"],
                    weaknesses=["비즈니스 임팩트 부족"],
                    improvement_suggestion="비즈니스 가치를 강조하세요",
                    improved_content="개선된 내용...",
                ),
                BlockReviewResponse(
                    block_id=block_id_2,
                    evaluation_summary="우수한 프로젝트입니다",
                    strengths=["명확한 문제 정의", "측정 가능한 성과"],
                    weaknesses=[],
                    improvement_suggestion="현재 수준을 유지하세요",
                ),
            ],
        )
        mock_review_service.review_section = AsyncMock(return_value=mock_response)

        # API 호출
        response = client_with_mock_service.post(
            f"/api/v1/resumes/{resume_id}/reviews/sections/project/{section_id}",
            json={
                "id": str(section_id),
                "type": "project",
                "title": "프로젝트",
                "orderIndex": 0,
                "blocks": [
                    {
                        "id": str(block_id_1),
                        "subTitle": "AI 챗봇 개발",
                        "period": "2023.01 - 2023.06",
                        "content": "FastAPI 기반 챗봇 백엔드 구축",
                        "isVisible": True,
                        "techStack": ["Python", "FastAPI"],
                    },
                    {
                        "id": str(block_id_2),
                        "subTitle": "추천 시스템 개발",
                        "period": "2023.07 - 2023.12",
                        "content": "머신러닝 기반 추천 알고리즘 구현",
                        "isVisible": True,
                        "techStack": ["Python", "scikit-learn"],
                    },
                ],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sectionId"] == str(section_id)
        assert data["targetType"] == "project"
        assert len(data["blockResults"]) == 2
        assert data["blockResults"][0]["blockId"] == str(block_id_1)

    def test_review_section_invalid_section_type(self, client: TestClient) -> None:
        """잘못된 섹션 타입."""
        resume_id = uuid4()
        section_id = uuid4()

        response = client.post(
            f"/api/v1/resumes/{resume_id}/reviews/sections/invalid_type/{section_id}",
            json={
                "id": str(section_id),
                "type": "project",
                "title": "프로젝트",
                "orderIndex": 0,
                "blocks": [],
            },
        )

        # 잘못된 enum 값
        assert response.status_code == 422


class TestReviewBlockEndpoint:
    """블록 리뷰 엔드포인트 테스트."""

    @pytest.mark.asyncio
    async def test_review_block_success(
        self, client_with_mock_service: TestClient, mock_review_service: MagicMock
    ) -> None:
        """블록 리뷰 성공."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id = uuid4()

        mock_response = ReviewResponse(
            resume_id=resume_id,
            target_type="project_block",
            evaluation_summary="구체적인 프로젝트입니다",
            strengths=["명확한 역할", "측정 가능한 성과"],
            weaknesses=["기술적 챌린지 설명 부족"],
            improvement_suggestion="기술적 어려움을 어떻게 해결했는지 추가하세요",
            improved_content="개선된 블록 내용...",
            block_id=block_id,
        )
        mock_review_service.review_block = AsyncMock(return_value=mock_response)

        response = client_with_mock_service.post(
            f"/api/v1/resumes/{resume_id}/reviews/sections/project/{section_id}/blocks/{block_id}",
            json={
                "id": str(block_id),
                "subTitle": "AI 챗봇 개발",
                "period": "2023.01 - 2023.06",
                "content": "FastAPI 기반 챗봇 백엔드 구축",
                "isVisible": True,
                "techStack": ["Python", "FastAPI", "PostgreSQL"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["blockId"] == str(block_id)
        assert data["targetType"] == "project_block"
        assert len(data["strengths"]) == 2


class TestReviewSummaryEndpoint:
    """전체 이력서 요약 리뷰 엔드포인트 테스트."""

    @pytest.mark.asyncio
    async def test_review_summary_success(
        self, client_with_mock_service: TestClient, mock_review_service: MagicMock
    ) -> None:
        """전체 이력서 리뷰 성공."""
        resume_id = uuid4()

        mock_response = ReviewResponse(
            resume_id=resume_id,
            target_type="resume_full",
            evaluation_summary="전체적으로 우수한 이력서입니다",
            strengths=["명확한 커리어 스토리", "다양한 프로젝트 경험", "구체적인 성과"],
            weaknesses=["일부 섹션 간 일관성 부족"],
            improvement_suggestion="전체적인 스토리라인을 더 강화하세요",
        )
        mock_review_service.review_summary = AsyncMock(return_value=mock_response)

        response = client_with_mock_service.post(
            f"/api/v1/resumes/{resume_id}/reviews/summary",
            json=create_full_resume_json(),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["targetType"] == "resume_full"
        assert len(data["strengths"]) == 3
