from enum import Enum


class SectionType(str, Enum):
    """이력서 리뷰 타입"""

    INTRODUCTION = "introduction"  # 간단 소개글
    WORK_EXPERIENCE = "work_experience"  # 경력 내용
    PROJECT = "project"  # 프로젝트 내용
    EDUCATION = "education"  # 교육 내용
    # SKILL = "skill"                    # 스킬 내용
