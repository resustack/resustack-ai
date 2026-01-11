from backend.domain.resume.models import Block, Resume, Section, Skills
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class ResumeReviewRequest(Resume):
    """이력서 리뷰 요청 모델"""

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class ResumeSectionReviewRequest(Section):
    """이력서 섹션 리뷰 요청 모델"""

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class ResumeBlockReviewRequest(Block):
    """이력서 블록 리뷰 요청 모델"""

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class ResumeSkillReviewRequest(BaseModel):
    """스킬 리뷰 요청 모델"""

    skills: Skills = Field(..., description="스킬")

    class Config:
        alias_generator = to_camel
        populate_by_name = True
