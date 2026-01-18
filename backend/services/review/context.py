"""Review Context - AI 리뷰 파이프라인의 입력 컨텍스트."""

from uuid import UUID

from pydantic import BaseModel, Field

from backend.domain.resume.enums import SectionType
from backend.services.review.enums import ReviewTargetType


class BlockData(BaseModel):
    """블록 데이터 (AI 컨텍스트용)."""

    block_id: UUID = Field(..., description="블록 ID")
    sub_title: str = Field(..., description="블록 부제목 (회사명, 프로젝트명 등)")
    period: str = Field(..., description="기간")
    content: str = Field(..., description="블록 주요 내용")
    tech_stack: list[str] = Field(default_factory=list, description="관련 기술 스택")
    link: str | None = Field(None, description="관련 링크")


class SectionData(BaseModel):
    """섹션 데이터 (AI 컨텍스트용)."""

    section_id: UUID = Field(..., description="섹션 ID")
    section_type: SectionType = Field(..., description="섹션 타입")
    title: str = Field(..., description="섹션 제목")
    blocks: list[BlockData] = Field(default_factory=list, description="블록 목록")


class IntroductionData(BaseModel):
    """소개글 데이터 (AI 컨텍스트용)."""

    name: str = Field(..., description="이름")
    position: str = Field(..., description="목표 직무")
    content: str = Field(..., description="현재 소개글")
    work_experience_summary: str = Field(default="", description="경력 요약")
    project_summary: str = Field(default="", description="프로젝트 요약")


class SkillData(BaseModel):
    """스킬 데이터 (AI 컨텍스트용)."""

    dev_ops: list[str] = Field(default_factory=list, description="DevOps 스킬")
    language: list[str] = Field(default_factory=list, description="프로그래밍 언어")
    framework: list[str] = Field(default_factory=list, description="프레임워크")
    database: list[str] = Field(default_factory=list, description="데이터베이스")
    tools: list[str] = Field(default_factory=list, description="도구")
    library: list[str] = Field(default_factory=list, description="라이브러리")
    testing: list[str] = Field(default_factory=list, description="테스팅 도구")
    collaboration: list[str] = Field(default_factory=list, description="협업 도구")


class ReviewContext(BaseModel):
    """AI 리뷰 파이프라인의 단일 입력 컨텍스트.

    모든 리뷰 요청은 이 모델로 변환되어 AI 체인에 전달됩니다.
    """

    resume_id: UUID = Field(..., description="이력서 ID")
    target_type: ReviewTargetType = Field(..., description="리뷰 대상 타입")

    # 선택적 데이터 (target_type에 따라 하나만 채워짐)
    introduction: IntroductionData | None = Field(None, description="소개글 데이터")
    skill: SkillData | None = Field(None, description="스킬 데이터")
    section: SectionData | None = Field(None, description="섹션 데이터")
    block: BlockData | None = Field(None, description="블록 데이터 (단일)")

    # 전체 리뷰용 (모든 데이터 포함)
    full_resume_text: str | None = Field(None, description="전체 이력서 텍스트 (요약)")
