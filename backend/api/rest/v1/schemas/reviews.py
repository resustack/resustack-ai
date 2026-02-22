from uuid import UUID

from backend.utils.schema_base import CamelModel
from pydantic import Field


class ReviewResponse(CamelModel):
    """리뷰 응답 모델 (공통)."""

    resume_id: UUID = Field(..., description="이력서 ID")
    target_type: str = Field(..., description="리뷰 대상 타입")
    evaluation_summary: str = Field(..., description="전반적인 평가 요약")
    strengths: list[str] = Field(default_factory=list, description="잘된 점 목록")
    weaknesses: list[str] = Field(default_factory=list, description="개선 필요점 목록")
    improvement_suggestion: str = Field(..., description="개선 제안 요약")
    improved_content: str | None = Field(None, description="개선된 문장/내용 (블록/아이템 리뷰 시)")
    block_id: UUID | None = Field(None, description="리뷰한 블록 ID (블록 리뷰 시)")


class BlockReviewResponse(CamelModel):
    """블록 리뷰 응답 (섹션 리뷰 결과 내 사용)."""

    block_id: UUID | None = Field(None, description="블록 ID")
    evaluation_summary: str = Field(..., description="블록 평가 요약")
    strengths: list[str] = Field(default_factory=list, description="잘된 점 목록")
    weaknesses: list[str] = Field(default_factory=list, description="개선 필요점 목록")
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
