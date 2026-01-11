from uuid import UUID

from backend.ai.output.review_result import ReviewResult, SectionReviewResult
from backend.utils.schema_base import CamelModel
from pydantic import Field


class ImprovementPointResponse(CamelModel):
    """개선 필요점 응답 모델."""

    problem: str = Field(..., description="구체적인 문제점")
    reason: str = Field(..., description="왜 문제인지 설명")


class ReviewResponse(CamelModel):
    """리뷰 응답 모델 (공통)."""

    resume_id: UUID = Field(..., description="이력서 ID")
    target_type: str = Field(..., description="리뷰 대상 타입")
    evaluation_summary: str = Field(..., description="전반적인 평가 요약")
    strengths: list[str] = Field(default_factory=list, description="잘된 점 목록")
    weaknesses: list[ImprovementPointResponse] = Field(
        default_factory=list, description="개선 필요점 목록"
    )
    improvement_suggestion: str = Field(..., description="개선 제안 요약")
    improved_content: str | None = Field(
        None, description="개선된 문장/내용 (블록/아이템 리뷰 시)"
    )
    block_id: UUID | None = Field(None, description="리뷰한 블록 ID (블록 리뷰 시)")


    @classmethod
    def from_review_result(cls, resume_id: UUID, result: ReviewResult) -> "ReviewResponse":
        """ReviewResult → ReviewResponse 변환."""
        return cls(
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


class BlockReviewResponse(CamelModel):
    """블록 리뷰 응답 (섹션 리뷰 결과 내 사용)."""

    block_id: UUID | None = Field(None, description="블록 ID")
    evaluation_summary: str = Field(..., description="블록 평가 요약")
    strengths: list[str] = Field(default_factory=list, description="잘된 점 목록")
    weaknesses: list[ImprovementPointResponse] = Field(
        default_factory=list, description="개선 필요점 목록"
    )
    improvement_suggestion: str = Field(..., description="개선 제안")
    improved_content: str | None = Field(None, description="개선된 내용")


class SectionReviewResponse(CamelModel):
    """섹션 리뷰 응답 모델."""

    resume_id: UUID = Field(..., description="이력서 ID")
    section_id: UUID = Field(..., description="섹션 ID")
    target_type: str = Field(..., description="리뷰 대상 타입")
    overall_evaluation: str = Field(..., description="섹션 전체 평가 요약")
    block_results: list[BlockReviewResponse] = Field(
        default_factory=list, description="각 블록별 리뷰 결과"
    )


    @classmethod
    def from_section_review_result(
        cls, resume_id: UUID, result: SectionReviewResult
    ) -> "SectionReviewResponse":
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

        return cls(
            resume_id=resume_id,
            section_id=result.section_id,
            target_type=result.target_type.value,
            overall_evaluation=result.overall_evaluation,
            block_results=block_responses,
        )
