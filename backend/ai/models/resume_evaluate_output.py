from pydantic import BaseModel, Field


class ImprovementPoint(BaseModel):
    """개선이 필요한 부분"""

    problem: str = Field(description="구체적인 문제점")
    reason: str = Field(description="왜 문제인지 설명")


class BlockEvaluation(BaseModel):
    """단일 block 평가 결과"""

    evaluation_summary: str = Field(description="현재 상태를 1-2문장으로 요약")
    improvement_needed: list[ImprovementPoint] = Field(description="문제점과 이유")
    improvement_suggestion: str = Field(description="개선 제안")


class SectionEvaluation(BaseModel):
    """섹션 평가 결과"""

    evaluations: list[BlockEvaluation] = Field(description="각 block별 평가 결과")
