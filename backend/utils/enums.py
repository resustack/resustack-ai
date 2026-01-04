from enum import StrEnum


class SectionType(StrEnum):
    """
    이력서 내부 섹션 타입
    - 섹션이라는 논리적 단위를 공통으로 사용하는 아이템 타입
    """

    WORK_EXPERIENCE = "work_experience"  # 경력 내용
    PROJECT = "project"  # 프로젝트 내용
    EDUCATION = "education"  # 교육 내용


class ResumeItemType(StrEnum):
    """
    이력서 내부 단일 아이템 타입
    - 이력서에서 섹션을 제외한 나머지 아이템 타입
    """

    INTRODUCTION = "introduction"  # 간단 소개글
    SKILL = "skill"  # 스킬
