"""Review Response Mapper.

AI output 모델을 API Response 모델로 변환합니다.
"""

from uuid import UUID

from backend.ai.output.review_result import ReviewResult, SectionReviewResult
from backend.api.rest.v1.schemas.reviews import (
    BlockReviewResponse,
    ImprovementPointResponse,
    ReviewResponse,
    SectionReviewResponse,
)


class ReviewResponseMapper:
    """리뷰 결과를 API Response로 변환하는 매퍼."""

    @staticmethod
    def to_review_response(resume_id: UUID, result: ReviewResult) -> ReviewResponse:
        """ReviewResult → ReviewResponse 변환."""
        return ReviewResponse(
            resume_id=resume_id,
            target_type=result.target_type.value,
            evaluation_summary=result.evaluation_summary,
            strengths=result.strengths,
            weaknesses=[
                ImprovementPointResponse(problem=w.problem, reason=w.reason)
                for w in result.weaknesses
            ],
            improvement_suggestion=result.improvement_suggestion,
            improved_content=result.improved_content,
            block_id=result.block_id,
        )

    @staticmethod
    def to_section_review_response(
        resume_id: UUID,
        result: SectionReviewResult,
    ) -> SectionReviewResponse:
        """SectionReviewResult → SectionReviewResponse 변환."""
        block_responses = [
            BlockReviewResponse(
                block_id=br.block_id,
                evaluation_summary=br.evaluation_summary,
                strengths=br.strengths,
                weaknesses=[
                    ImprovementPointResponse(problem=w.problem, reason=w.reason)
                    for w in br.weaknesses
                ],
                improvement_suggestion=br.improvement_suggestion,
                improved_content=br.improved_content,
            )
            for br in result.block_results
        ]

        return SectionReviewResponse(
            resume_id=resume_id,
            section_id=result.section_id,
            target_type=result.target_type.value,
            overall_evaluation=result.overall_evaluation,
            block_results=block_responses,
        )
