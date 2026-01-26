"""리뷰 서비스 테스트."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from backend.ai.output.review_result import ReviewResult
from backend.api.rest.v1.schemas.resumes import (
    ResumeBlockReviewRequest,
    ResumeReviewRequest,
    ResumeSectionReviewRequest,
    ResumeSkillReviewRequest,
)
from backend.domain.resume.enums import SectionType
from backend.domain.resume.models import Block, Profile, Section, Skills
from backend.services.review.assembler import ReviewContextAssembler
from backend.services.review.context import ReviewContext
from backend.services.review.enums import ReviewTargetType
from backend.services.review.mapper import ReviewResponseMapper
from backend.services.review.service import ReviewService


def create_resume_review_request(
    profile: Profile,
    sections: list[Section] | None = None,
    skills: Skills | None = None,
) -> ResumeReviewRequest:
    """ResumeReviewRequest 헬퍼 함수."""
    now = datetime.now()
    return ResumeReviewRequest(
        _id="507f1f77bcf86cd799439011",
        user_id=1,
        title="테스트 이력서",
        template_id=1,
        status="draft",
        is_public=False,
        profile=profile,
        sections=sections or [],
        skills=skills or Skills(),
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def mock_assembler() -> MagicMock:
    """Mock ReviewContextAssembler."""
    return MagicMock(spec=ReviewContextAssembler)


@pytest.fixture
def mock_chain() -> MagicMock:
    """Mock ReviewChain."""
    chain = MagicMock()
    chain.run = AsyncMock()
    return chain


@pytest.fixture
def mock_section_chain() -> MagicMock:
    """Mock SectionReviewChain."""
    chain = MagicMock()
    chain.run = AsyncMock()
    return chain


@pytest.fixture
def mock_mapper() -> MagicMock:
    """Mock ReviewResponseMapper."""
    return MagicMock(spec=ReviewResponseMapper)


@pytest.fixture
def review_service(
    mock_assembler: MagicMock,
    mock_chain: MagicMock,
    mock_section_chain: MagicMock,
    mock_mapper: MagicMock,
) -> ReviewService:
    """ReviewService 인스턴스."""
    return ReviewService(
        assembler=mock_assembler,
        chain=mock_chain,
        section_chain=mock_section_chain,
        mapper=mock_mapper,
    )


@pytest.fixture
def sample_profile() -> Profile:
    """샘플 Profile."""
    return Profile(
        name="홍길동",
        position="백엔드 개발자",
        introduction="FastAPI 전문 개발자입니다.",
        email="hong@example.com",
        phone="010-1234-5678",
    )


@pytest.fixture
def sample_skills() -> Skills:
    """샘플 Skills."""
    return Skills(
        language=["Python", "TypeScript"],
        framework=["FastAPI", "React"],
        database=["PostgreSQL", "Redis"],
    )


class TestReviewServiceSummary:
    """전체 이력서 요약 리뷰 서비스 테스트."""

    @pytest.mark.asyncio
    async def test_review_summary_success(
        self,
        review_service: ReviewService,
        mock_assembler: MagicMock,
        mock_chain: MagicMock,
        mock_mapper: MagicMock,
        sample_profile: Profile,
    ) -> None:
        """전체 이력서 리뷰 성공."""
        resume_id = uuid4()
        request = create_resume_review_request(profile=sample_profile)

        # Mock 설정
        mock_context = ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.RESUME_FULL,
            full_resume_text="이력서 전체 내용",
        )
        mock_assembler.assemble_full.return_value = mock_context

        mock_result = ReviewResult(
            target_type=ReviewTargetType.RESUME_FULL,
            evaluation_summary="우수한 이력서",
            strengths=["명확한 목표"],
            weaknesses=["개선 필요"],
            improvement_suggestion="제안사항",
        )
        mock_chain.run.return_value = mock_result

        # 실행
        await review_service.review_summary(resume_id, request)

        # 검증
        mock_assembler.assemble_full.assert_called_once_with(resume_id, request)
        mock_chain.run.assert_called_once_with(mock_context)
        mock_mapper.to_review_response.assert_called_once_with(resume_id, mock_result)

    @pytest.mark.asyncio
    async def test_review_summary_chain_exception(
        self,
        review_service: ReviewService,
        mock_assembler: MagicMock,
        mock_chain: MagicMock,
        sample_profile: Profile,
    ) -> None:
        """체인 실행 중 예외 발생."""
        resume_id = uuid4()
        request = create_resume_review_request(profile=sample_profile)

        mock_context = ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.RESUME_FULL,
            full_resume_text="내용",
        )
        mock_assembler.assemble_full.return_value = mock_context
        mock_chain.run.side_effect = Exception("AI 서비스 오류")

        # 예외 발생 확인
        with pytest.raises(Exception, match="AI 서비스 오류"):
            await review_service.review_summary(resume_id, request)


class TestReviewServiceIntroduction:
    """소개글 리뷰 서비스 테스트."""

    @pytest.mark.asyncio
    async def test_review_introduction_success(
        self,
        review_service: ReviewService,
        mock_assembler: MagicMock,
        mock_chain: MagicMock,
        mock_mapper: MagicMock,
        sample_profile: Profile,
    ) -> None:
        """소개글 리뷰 성공."""
        resume_id = uuid4()
        request = create_resume_review_request(profile=sample_profile)

        mock_context = ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.INTRODUCTION,
        )
        mock_assembler.assemble_introduction.return_value = mock_context

        mock_result = ReviewResult(
            target_type=ReviewTargetType.INTRODUCTION,
            evaluation_summary="명확한 소개글",
            strengths=["구체적인 기술 스택"],
            weaknesses=["차별화 부족"],
            improvement_suggestion="경험을 추가하세요",
            improved_content="개선된 소개글...",
        )
        mock_chain.run.return_value = mock_result

        # 실행
        await review_service.review_introduction(resume_id, request)

        # 검증
        mock_assembler.assemble_introduction.assert_called_once_with(resume_id, request)
        mock_chain.run.assert_called_once()


class TestReviewServiceSkill:
    """스킬 리뷰 서비스 테스트."""

    @pytest.mark.asyncio
    async def test_review_skill_success(
        self,
        review_service: ReviewService,
        mock_assembler: MagicMock,
        mock_chain: MagicMock,
        mock_mapper: MagicMock,
        sample_skills: Skills,
    ) -> None:
        """스킬 리뷰 성공."""
        resume_id = uuid4()
        request = ResumeSkillReviewRequest(skills=sample_skills)

        mock_context = ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.SKILL,
        )
        mock_assembler.assemble_skill.return_value = mock_context

        mock_result = ReviewResult(
            target_type=ReviewTargetType.SKILL,
            evaluation_summary="균형잡힌 스킬셋",
            strengths=["풀스택 역량"],
            weaknesses=["전문성 깊이"],
            improvement_suggestion="특정 분야 집중",
        )
        mock_chain.run.return_value = mock_result

        # 실행
        await review_service.review_skill(resume_id, request)

        # 검증
        mock_assembler.assemble_skill.assert_called_once_with(resume_id, request)
        mock_mapper.to_review_response.assert_called_once()


class TestReviewServiceSection:
    """섹션 리뷰 서비스 테스트."""

    @pytest.mark.asyncio
    async def test_review_section_success(
        self,
        review_service: ReviewService,
        mock_assembler: MagicMock,
        mock_section_chain: MagicMock,
        mock_mapper: MagicMock,
        sample_profile: Profile,
    ) -> None:
        """섹션 리뷰 성공."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id_1 = uuid4()
        block_id_2 = uuid4()

        blocks = [
            Block(
                id=block_id_1,
                sub_title="프로젝트 1",
                period="2023.01 - 2023.06",
                content="내용 1",
                is_visible=True,
            ),
            Block(
                id=block_id_2,
                sub_title="프로젝트 2",
                period="2023.07 - 2023.12",
                content="내용 2",
                is_visible=True,
            ),
        ]

        request = ResumeSectionReviewRequest(
            id=section_id,
            type=SectionType.PROJECT,
            title="프로젝트",
            order_index=0,
            blocks=blocks,
            profile=sample_profile,
        )

        # Mock 설정
        mock_context = ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.PROJECT,
        )
        mock_assembler.assemble_section.return_value = mock_context

        block_results = [
            ReviewResult(
                target_type=ReviewTargetType.PROJECT,
                evaluation_summary="우수한 프로젝트 1",
                strengths=["구체적"],
                weaknesses=[],
                improvement_suggestion="유지",
                block_id=block_id_1,
            ),
            ReviewResult(
                target_type=ReviewTargetType.PROJECT,
                evaluation_summary="우수한 프로젝트 2",
                strengths=["명확함"],
                weaknesses=[],
                improvement_suggestion="유지",
                block_id=block_id_2,
            ),
        ]
        mock_section_chain.run.return_value = block_results

        # 실행
        _ = await review_service.review_section(
            resume_id, SectionType.PROJECT, request
        )

        # 검증
        mock_assembler.assemble_section.assert_called_once_with(
            resume_id, SectionType.PROJECT, request
        )
        mock_section_chain.run.assert_called_once()
        mock_mapper.to_section_review_response.assert_called_once()

    def test_summarize_block_results_empty(self, review_service: ReviewService) -> None:
        """블록 결과가 비어있을 때."""
        result = review_service._summarize_block_results([])
        assert result == "평가할 블록이 없습니다."

    def test_summarize_block_results_multiple(self, review_service: ReviewService) -> None:
        """여러 블록 결과 요약."""
        block_results = [
            ReviewResult(
                target_type=ReviewTargetType.PROJECT,
                evaluation_summary="프로젝트 1 평가",
                strengths=[],
                weaknesses=[],
                improvement_suggestion="",
            ),
            ReviewResult(
                target_type=ReviewTargetType.PROJECT,
                evaluation_summary="프로젝트 2 평가",
                strengths=[],
                weaknesses=[],
                improvement_suggestion="",
            ),
        ]

        result = review_service._summarize_block_results(block_results)

        assert "1. 프로젝트 1 평가" in result
        assert "2. 프로젝트 2 평가" in result


class TestReviewServiceBlock:
    """블록 리뷰 서비스 테스트."""

    @pytest.mark.asyncio
    async def test_review_block_success(
        self,
        review_service: ReviewService,
        mock_assembler: MagicMock,
        mock_chain: MagicMock,
        mock_mapper: MagicMock,
        sample_profile: Profile,
    ) -> None:
        """블록 리뷰 성공."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id = uuid4()

        block = Block(
            id=block_id,
            sub_title="AI 챗봇 개발",
            period="2023.01 - 2023.06",
            content="FastAPI 기반 챗봇 구축",
            is_visible=True,
            tech_stack=["Python", "FastAPI"],
        )

        request = ResumeBlockReviewRequest(
            id=block_id,
            sub_title=block.sub_title,
            period=block.period,
            content=block.content,
            is_visible=block.is_visible,
            tech_stack=block.tech_stack,
            profile=sample_profile,
        )

        # Mock 설정
        mock_context = ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.PROJECT_BLOCK,
        )
        mock_assembler.assemble_block.return_value = mock_context

        mock_result = ReviewResult(
            target_type=ReviewTargetType.PROJECT_BLOCK,
            evaluation_summary="구체적인 프로젝트",
            strengths=["기술 스택 명확"],
            weaknesses=["성과 지표 부족"],
            improvement_suggestion="수치화된 성과 추가",
            improved_content="개선된 내용...",
            block_id=block_id,
        )
        mock_chain.run.return_value = mock_result

        # 실행
        await review_service.review_block(
            resume_id,
            SectionType.PROJECT,
            section_id,
            block_id,
            request,
        )

        # 검증
        mock_assembler.assemble_block.assert_called_once_with(
            resume_id, SectionType.PROJECT, section_id, block_id, request
        )
        mock_chain.run.assert_called_once()
        mock_mapper.to_review_response.assert_called_once()
