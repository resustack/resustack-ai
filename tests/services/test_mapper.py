"""ReviewResponseMapper 테스트."""

from uuid import uuid4

import pytest

from backend.ai.output.review_result import ReviewResult, SectionReviewResult
from backend.services.review.enums import ReviewTargetType
from backend.services.review.mapper import (
    ReviewResponseMapper,
    get_review_response_mapper,
)


@pytest.fixture
def mapper() -> ReviewResponseMapper:
    """ReviewResponseMapper 인스턴스."""
    return ReviewResponseMapper()


class TestToReviewResponse:
    """ReviewResult → ReviewResponse 변환 테스트."""

    def test_basic_conversion(self, mapper: ReviewResponseMapper) -> None:
        """기본 변환 테스트."""
        resume_id = uuid4()
        result = ReviewResult(
            target_type=ReviewTargetType.INTRODUCTION,
            evaluation_summary="명확한 소개글입니다",
            strengths=["구체적인 기술 스택", "명확한 경력"],
            weaknesses=["차별화 포인트 부족"],
            improvement_suggestion="본인만의 강점을 추가하세요",
            improved_content="개선된 소개글...",
        )

        response = mapper.to_review_response(resume_id, result)

        assert response.resume_id == resume_id
        assert response.target_type == "introduction"
        assert response.evaluation_summary == "명확한 소개글입니다"
        assert response.strengths == ["구체적인 기술 스택", "명확한 경력"]
        assert response.weaknesses == ["차별화 포인트 부족"]
        assert response.improvement_suggestion == "본인만의 강점을 추가하세요"
        assert response.improved_content == "개선된 소개글..."

    def test_conversion_with_block_id(self, mapper: ReviewResponseMapper) -> None:
        """블록 ID가 포함된 변환 테스트."""
        resume_id = uuid4()
        block_id = uuid4()
        result = ReviewResult(
            target_type=ReviewTargetType.PROJECT_BLOCK,
            evaluation_summary="우수한 프로젝트입니다",
            strengths=["명확한 성과"],
            weaknesses=[],
            improvement_suggestion="현재 수준 유지",
            block_id=block_id,
        )

        response = mapper.to_review_response(resume_id, result)

        assert response.block_id == block_id
        assert response.target_type == "project_block"

    def test_conversion_without_improved_content(
        self, mapper: ReviewResponseMapper
    ) -> None:
        """개선된 내용이 없는 경우 테스트."""
        resume_id = uuid4()
        result = ReviewResult(
            target_type=ReviewTargetType.SKILL,
            evaluation_summary="균형잡힌 스킬셋입니다",
            strengths=["풀스택 역량"],
            weaknesses=["전문성 깊이"],
            improvement_suggestion="특정 분야 집중 추천",
            improved_content=None,
        )

        response = mapper.to_review_response(resume_id, result)

        assert response.improved_content is None

    def test_conversion_empty_lists(self, mapper: ReviewResponseMapper) -> None:
        """빈 리스트 처리 테스트."""
        resume_id = uuid4()
        result = ReviewResult(
            target_type=ReviewTargetType.RESUME_FULL,
            evaluation_summary="전반적으로 우수합니다",
            strengths=[],
            weaknesses=[],
            improvement_suggestion="현재 상태 유지",
        )

        response = mapper.to_review_response(resume_id, result)

        assert response.strengths == []
        assert response.weaknesses == []

    def test_conversion_all_target_types(self, mapper: ReviewResponseMapper) -> None:
        """모든 target_type 변환 테스트."""
        resume_id = uuid4()
        target_types = [
            ReviewTargetType.INTRODUCTION,
            ReviewTargetType.SKILL,
            ReviewTargetType.RESUME_FULL,
            ReviewTargetType.PROJECT,
            ReviewTargetType.WORK_EXPERIENCE,
            ReviewTargetType.EDUCATION,
            ReviewTargetType.PROJECT_BLOCK,
            ReviewTargetType.WORK_EXPERIENCE_BLOCK,
            ReviewTargetType.EDUCATION_BLOCK,
        ]

        for target_type in target_types:
            result = ReviewResult(
                target_type=target_type,
                evaluation_summary="테스트",
                strengths=["강점"],
                weaknesses=["약점"],
                improvement_suggestion="제안",
            )

            response = mapper.to_review_response(resume_id, result)

            assert response.target_type == target_type.value


class TestToSectionReviewResponse:
    """SectionReviewResult → SectionReviewResponse 변환 테스트."""

    def test_basic_section_conversion(self, mapper: ReviewResponseMapper) -> None:
        """기본 섹션 변환 테스트."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id_1 = uuid4()
        block_id_2 = uuid4()

        result = SectionReviewResult(
            target_type=ReviewTargetType.PROJECT,
            section_id=section_id,
            overall_evaluation="다양한 프로젝트 경험이 있습니다",
            block_results=[
                ReviewResult(
                    target_type=ReviewTargetType.PROJECT_BLOCK,
                    evaluation_summary="프로젝트 1 평가",
                    strengths=["구체적인 성과"],
                    weaknesses=["기술 스택 설명 부족"],
                    improvement_suggestion="기술적 깊이 추가",
                    improved_content="개선된 프로젝트 1...",
                    block_id=block_id_1,
                ),
                ReviewResult(
                    target_type=ReviewTargetType.PROJECT_BLOCK,
                    evaluation_summary="프로젝트 2 평가",
                    strengths=["명확한 역할"],
                    weaknesses=[],
                    improvement_suggestion="현재 수준 유지",
                    block_id=block_id_2,
                ),
            ],
        )

        response = mapper.to_section_review_response(resume_id, result)

        assert response.resume_id == resume_id
        assert response.section_id == section_id
        assert response.target_type == "project"
        assert response.overall_evaluation == "다양한 프로젝트 경험이 있습니다"
        assert len(response.block_results) == 2
        assert response.block_results[0].block_id == block_id_1
        assert response.block_results[0].evaluation_summary == "프로젝트 1 평가"
        assert response.block_results[1].block_id == block_id_2

    def test_section_conversion_empty_blocks(
        self, mapper: ReviewResponseMapper
    ) -> None:
        """블록이 없는 섹션 변환 테스트."""
        resume_id = uuid4()
        section_id = uuid4()

        result = SectionReviewResult(
            target_type=ReviewTargetType.WORK_EXPERIENCE,
            section_id=section_id,
            overall_evaluation="경력 섹션이 비어있습니다",
            block_results=[],
        )

        response = mapper.to_section_review_response(resume_id, result)

        assert response.section_id == section_id
        assert response.target_type == "work_experience"
        assert len(response.block_results) == 0

    def test_section_conversion_block_details(
        self, mapper: ReviewResponseMapper
    ) -> None:
        """블록 상세 정보 변환 테스트."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id = uuid4()

        block_result = ReviewResult(
            target_type=ReviewTargetType.EDUCATION_BLOCK,
            evaluation_summary="학력 블록 평가",
            strengths=["관련 전공", "높은 학점"],
            weaknesses=["활동 내역 부족"],
            improvement_suggestion="동아리, 프로젝트 활동 추가",
            improved_content="개선된 학력 설명...",
            block_id=block_id,
        )

        result = SectionReviewResult(
            target_type=ReviewTargetType.EDUCATION,
            section_id=section_id,
            overall_evaluation="학력 섹션 평가",
            block_results=[block_result],
        )

        response = mapper.to_section_review_response(resume_id, result)

        block_response = response.block_results[0]
        assert block_response.block_id == block_id
        assert block_response.evaluation_summary == "학력 블록 평가"
        assert block_response.strengths == ["관련 전공", "높은 학점"]
        assert block_response.weaknesses == ["활동 내역 부족"]
        assert block_response.improvement_suggestion == "동아리, 프로젝트 활동 추가"
        assert block_response.improved_content == "개선된 학력 설명..."

    def test_section_conversion_multiple_blocks(
        self, mapper: ReviewResponseMapper
    ) -> None:
        """여러 블록이 있는 섹션 변환 테스트."""
        resume_id = uuid4()
        section_id = uuid4()

        block_results = [
            ReviewResult(
                target_type=ReviewTargetType.PROJECT_BLOCK,
                evaluation_summary=f"블록 {i} 평가",
                strengths=[f"강점 {i}"],
                weaknesses=[f"약점 {i}"],
                improvement_suggestion=f"제안 {i}",
                block_id=uuid4(),
            )
            for i in range(1, 6)
        ]

        result = SectionReviewResult(
            target_type=ReviewTargetType.PROJECT,
            section_id=section_id,
            overall_evaluation="5개 프로젝트 섹션 평가",
            block_results=block_results,
        )

        response = mapper.to_section_review_response(resume_id, result)

        assert len(response.block_results) == 5
        for i, block_resp in enumerate(response.block_results, start=1):
            assert block_resp.evaluation_summary == f"블록 {i} 평가"
            assert block_resp.strengths == [f"강점 {i}"]


class TestGetReviewResponseMapper:
    """싱글톤 인스턴스 테스트."""

    def test_singleton_instance(self) -> None:
        """같은 인스턴스가 반환되는지 확인."""
        instance1 = get_review_response_mapper()
        instance2 = get_review_response_mapper()

        assert instance1 is instance2
        assert isinstance(instance1, ReviewResponseMapper)
