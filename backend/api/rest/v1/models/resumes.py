from pydantic import BaseModel, Field
from pydantic_core import Url

from backend.api.rest.v1.schemas.resumes import ResumeReviewResponse


class WorkExperience(BaseModel):
    """경력 도메인 모델"""

    company_name: str = Field(..., description="회사명")
    period: str = Field(..., description="재직 기간")
    tech_stack: list[str] = Field(..., description="관련 기술 스택")
    link: Url | None = Field(None, description="관련 링크")
    content: str = Field(..., description="경력 내용")


class Project(BaseModel):
    """프로젝트 도메인 모델"""

    project_title: str = Field(..., description="프로젝트 제목")
    period: str = Field(..., description="프로젝트 기간")
    tech_stack: list[str] = Field(..., description="기술 스택")
    link: Url | None = Field(None, description="프로젝트 링크")
    content: str = Field(..., description="프로젝트 내용")


class Education(BaseModel):
    """교육 도메인 모델"""

    education_name: str = Field(..., description="교육명/과정명")
    period: str = Field(..., description="교육 기간")
    tech_stack: list[str] = Field(..., description="학습한 기술")
    link: Url | None = Field(None, description="수료증/링크")
    position: str = Field(..., description="목표 직무")
    content: str = Field(..., description="교육 내용")


class Introduction(BaseModel):
    """소개글 도메인 모델"""

    name: str = Field(..., description="이름")
    position: str = Field(..., description="직무")
    work_experiences: list[WorkExperience] = Field(..., description="경력 내용들")
    projects: list[Project] = Field(..., description="프로젝트 내용들")
    content: str = Field(..., description="현재 소개글")


class TechSkill(BaseModel):
    """기술 스킬 도메인 모델"""

    dev_ops: list[str] = Field(..., description="DevOps 스킬")
    language: list[str] = Field(..., description="프로그래밍 언어")
    framework: list[str] = Field(..., description="프레임워크")
    database: list[str] = Field(..., description="데이터베이스")
    tools: list[str] = Field(..., description="도구")
    library: list[str] = Field(..., description="라이브러리")
    testing: list[str] = Field(..., description="테스팅 도구")
    collaboration: list[str] = Field(..., description="협업 도구")


class AIReviewResult(ResumeReviewResponse):
    """AI 리뷰 결과 모델"""
