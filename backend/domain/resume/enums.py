"""Domain Resume Enums."""

from enum import StrEnum


class SectionType(StrEnum):
    """이력서 내부 섹션 타입."""

    WORK_EXPERIENCE = "work_experience"
    PROJECT = "project"
    EDUCATION = "education"


class ResumeItemType(StrEnum):
    """이력서 내부 단일 아이템 타입."""

    INTRODUCTION = "introduction"
    SKILL = "skill"
