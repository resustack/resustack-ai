from uuid import UUID

from fastapi import APIRouter, Depends, status

from backend.api.rest.v1.schemas.resumes import (
    ResumeReviewRequest,
    ResumeReviewResponse,
    ResumeSectionReviewRequest,
    ResumeSkillReviewRequest,
)
from backend.services.dependency import (
    ResumeReviewService,
    get_introduction_review_service,
    get_resume_review_service,
    get_section_review_service,
    get_skill_review_service,
)
from backend.utils.enums import SectionType

router = APIRouter(prefix="/{resume_id}", tags=["resumes"])


@router.post(
    "/review",
    response_model=ResumeReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="이력서 전체 리뷰",
    description="이력서 전체를 리뷰하여 개선 제안을 반환합니다.",
)
async def review_resume(
    resume_id: UUID,
    request: ResumeReviewRequest,
    service: ResumeReviewService = Depends(get_resume_review_service),
) -> ResumeReviewResponse:
    """
    이력서 전체 리뷰

    Args:
        request: 이력서 리뷰 요청 데이터

    Returns:
        ResumeReviewResponse: 리뷰 결과 및 개선 제안
    """

    resume_review = await service.review_resume_all(resume_id, request)

    return ResumeReviewResponse(
        resume_id=resume_id,
        evaluation_result=resume_review.evaluation_result,
        improvement_suggestion=resume_review.improvement_suggestion,
        improved_resume_blocks_content=resume_review.improved_resume_blocks_content,
    )


@router.post(
    "/review/sections/{section_type}/{section_id}",
    response_model=ResumeReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="이력서 섹션 리뷰",
    description="이력서의 특정 섹션(경력, 프로젝트, 교육)을 리뷰하여 개선 제안을 반환합니다."
)
async def review_resume_section(
    resume_id: UUID,
    section_type: SectionType,
    section_id: UUID,
    request: ResumeSectionReviewRequest,
    service: ResumeReviewService = Depends(get_section_review_service),
) -> ResumeReviewResponse:
    """
    이력서 섹션 리뷰

    Args:
        section_type: 평가할 섹션 타입 (work_experience, project, education)
        section_id: 평가할 섹션 ID
        request: 섹션 리뷰 요청 데이터

    Returns:
        ResumeReviewResponse: 평가 결과 및 개선 제안
    """

    section_review = await service.review_resume_section(resume_id, request)

    return ResumeReviewResponse(
        resume_id=resume_id,
        evaluation_result=section_review.evaluation_result,
        improvement_suggestion=section_review.improvement_suggestion,
        improved_resume_blocks_content=section_review.improved_resume_blocks_content,
    )


@router.post(
    "/review/introduction",
    response_model=ResumeReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="소개글 리뷰",
    description="소개글을 리뷰하여 개선 제안을 반환합니다.",
)
async def review_resume_introduction(
    resume_id: UUID,
    request: ResumeReviewRequest,
    service: ResumeReviewService = Depends(get_introduction_review_service),
) -> ResumeReviewResponse:
    """
    소개글 리뷰
    """

    introduction_review = await service.review_resume_introduction(resume_id, request)

    return ResumeReviewResponse(
        resume_id=resume_id,
        evaluation_result=introduction_review.evaluation_result,
        improvement_suggestion=introduction_review.improvement_suggestion,
        improved_resume_blocks_content=introduction_review.improved_resume_blocks_content,
    )


@router.post(
    "/review/skill",
    response_model=ResumeReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="스킬 리뷰",
    description="스킬을 리뷰하여 개선 제안을 반환합니다.",
)
async def review_resume_skill(
    resume_id: UUID,
    request: ResumeSkillReviewRequest,
    service: ResumeReviewService = Depends(get_skill_review_service),
) -> ResumeReviewResponse:
    """
    스킬 리뷰
    """

    skill_review = await service.review_resume_skill(resume_id, request)

    return ResumeReviewResponse(
        resume_id=resume_id,
        evaluation_result=skill_review.evaluation_result,
        improvement_suggestion=skill_review.improvement_suggestion,
        improved_resume_blocks_content=skill_review.improved_resume_blocks_content,
    )
