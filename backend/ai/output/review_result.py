from uuid import UUID

from pydantic import BaseModel, Field

from backend.services.review.enums import ReviewTargetType


class EvaluationResult(BaseModel):
    """1단계 평가 결과 (개선안 제외)."""

    target_type: ReviewTargetType = Field(..., description="리뷰 대상 타입")
    summary: str = Field(..., description="전반적인 평가 요약")
    strengths: list[str] = Field(..., max_length=3, description="잘된 점 목록")
    weaknesses: list[str] = Field(..., max_length=3, description="개선 필요점 목록")
    block_id: UUID | None = Field(None, description="리뷰한 블록 ID")


class ReviewResult(BaseModel):
    """AI 리뷰 결과 (공통 응답 모델).

    모든 리뷰 결과는 이 모델로 반환됩니다.
    """

    target_type: ReviewTargetType = Field(..., description="리뷰 대상 타입")
    evaluation_summary: str = Field(..., description="전반적인 평가 요약")
    strengths: list[str] = Field(..., max_length=3, description="잘된 점 목록")
    weaknesses: list[str] = Field(..., max_length=3, description="개선 필요점 목록")
    improvement_suggestion: str = Field(..., description="개선 제안 요약")
    improved_content: str | None = Field(None, description="개선된 문장/내용 (블록/아이템 리뷰 시)")
    block_id: UUID | None = Field(None, description="리뷰한 블록 ID")


class SectionReviewResult(BaseModel):
    """섹션 리뷰 결과 (여러 블록 포함)."""

    target_type: ReviewTargetType = Field(..., description="리뷰 대상 타입")
    section_id: UUID = Field(..., description="섹션 ID")
    overall_evaluation: str = Field(..., description="섹션 전체 평가")
    block_results: list[ReviewResult] = Field(
        default_factory=list, description="각 블록별 리뷰 결과"
    )
