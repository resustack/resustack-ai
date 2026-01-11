from pydantic import Field

from backend.domain.resume.models import Block, Resume, Section, Skills
from backend.utils.schema_base import CamelCaseMixin, CamelModel


class ResumeReviewRequest(CamelCaseMixin, Resume):
    """이력서 리뷰 요청 모델."""

    pass


class ResumeSectionReviewRequest(CamelCaseMixin, Section):
    """이력서 섹션 리뷰 요청 모델."""

    pass


class ResumeBlockReviewRequest(CamelCaseMixin, Block):
    """이력서 블록 리뷰 요청 모델."""

    pass


class ResumeSkillReviewRequest(CamelModel):
    """스킬 리뷰 요청 모델."""

    skills: Skills = Field(..., description="스킬")
