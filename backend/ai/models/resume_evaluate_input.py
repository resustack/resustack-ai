from pydantic import BaseModel, Field
from pydantic_core import Url

from backend.utils.enums import SectionType


class IntroductionBlockInput(BaseModel):
    """소개글 평가 입력 데이터"""

    name: str = Field(..., description="이름")
    position: str = Field(..., description="직무")
    work_experience: str = Field(..., description="경력 요약")
    project: str = Field(..., description="프로젝트 요약")
    introduction: str = Field(..., description="현재 소개글")


class WorkExperienceBlockInput(BaseModel):
    """경력 평가 입력 데이터"""

    company_name: str = Field(..., description="회사명")
    period: str = Field(..., description="재직 기간")
    tech_stack: list[str] = Field(..., description="기술 스택")
    link: Url | None = Field(None, description="관련 링크")
    content: str = Field(..., description="경력 내용")


class ProjectBlockInput(BaseModel):
    """프로젝트 평가 입력 데이터"""

    project_title: str = Field(..., description="프로젝트 제목")
    period: str = Field(..., description="프로젝트 기간")
    tech_stack: list[str] = Field(..., description="기술 스택")
    link: Url | None = Field(None, description="프로젝트 링크")
    content: str = Field(..., description="프로젝트 내용")


class EducationBlockInput(BaseModel):
    """교육 평가 입력 데이터"""

    education_name: str = Field(..., description="교육명/과정명")
    period: str = Field(..., description="교육 기간")
    tech_stack: list[str] = Field(..., description="학습한 기술")
    link: Url | None = Field(None, description="수료증/링크")
    position: str = Field(..., description="목표 직무")
    content: str = Field(..., description="교육 내용")


# 타입 매핑
SECTION_INPUT_MAP = {
    SectionType.INTRODUCTION: IntroductionBlockInput,
    SectionType.WORK_EXPERIENCE: WorkExperienceBlockInput,
    SectionType.PROJECT: ProjectBlockInput,
    SectionType.EDUCATION: EducationBlockInput,
}
