from uuid import UUID

from backend.services.resume_service import ResumeReviewService
from backend.utils.enums import ResumeItemType, SectionType


def get_resume_review_service() -> ResumeReviewService:
    """전체 리뷰용 서비스"""
    return ResumeReviewService()


def get_section_review_service(
    section_type: SectionType,
    section_id: UUID,
) -> ResumeReviewService:
    """섹션 리뷰용 서비스 (path parameter 자동 주입)"""
    return ResumeReviewService(section_type, section_id)


def get_introduction_review_service() -> ResumeReviewService:
    """소개글 리뷰용 서비스"""
    return ResumeReviewService(ResumeItemType.INTRODUCTION)


def get_skill_review_service() -> ResumeReviewService:
    """스킬 리뷰용 서비스"""
    return ResumeReviewService(ResumeItemType.SKILL)
