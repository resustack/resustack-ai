"""Review Service Enums."""

from enum import StrEnum

from backend.domain.resume.enums import ResumeItemType, SectionType


class ReviewTargetType(StrEnum):
    """리뷰 대상 타입."""

    # 전체
    RESUME_FULL = "resume_full"

    # 아이템
    INTRODUCTION = "introduction"
    SKILL = "skill"

    # 섹션
    WORK_EXPERIENCE = "work_experience"
    PROJECT = "project"
    EDUCATION = "education"

    # 블록
    WORK_EXPERIENCE_BLOCK = "work_experience_block"
    PROJECT_BLOCK = "project_block"
    EDUCATION_BLOCK = "education_block"

    @classmethod
    def from_section_type(cls, section_type: SectionType) -> "ReviewTargetType":
        """SectionType을 ReviewTargetType으로 변환."""
        mapping = {
            SectionType.WORK_EXPERIENCE: cls.WORK_EXPERIENCE,
            SectionType.PROJECT: cls.PROJECT,
            SectionType.EDUCATION: cls.EDUCATION,
        }
        return mapping[section_type]

    @classmethod
    def from_section_type_block(cls, section_type: SectionType) -> "ReviewTargetType":
        """SectionType을 Block용 ReviewTargetType으로 변환."""
        mapping = {
            SectionType.WORK_EXPERIENCE: cls.WORK_EXPERIENCE_BLOCK,
            SectionType.PROJECT: cls.PROJECT_BLOCK,
            SectionType.EDUCATION: cls.EDUCATION_BLOCK,
        }
        return mapping[section_type]

    @classmethod
    def from_item_type(cls, item_type: ResumeItemType) -> "ReviewTargetType":
        """ResumeItemType을 ReviewTargetType으로 변환."""
        mapping = {
            ResumeItemType.INTRODUCTION: cls.INTRODUCTION,
            ResumeItemType.SKILL: cls.SKILL,
        }
        return mapping[item_type]
