import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status

from backend.api.rest.v1.schemas.resumes import (
    ResumeBlockReviewRequest,
    ResumeReviewRequest,
    ResumeSectionReviewRequest,
    ResumeSkillReviewRequest,
)
from backend.api.rest.v1.schemas.reviews import ReviewResponse, SectionReviewResponse
from backend.domain.resume.enums import SectionType
from backend.services import get_review_service
from backend.services import ReviewService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/{resume_id}/reviews", tags=["AI Reviews"])

@router.post(
    "/introduction",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="소개글 리뷰",
    description="이력서 소개글을 평가하고 개선된 버전을 제안합니다.",
)
async def review_introduction(
    resume_id: UUID,
    request: ResumeReviewRequest,
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    """소개글 리뷰.

    핵심 역량 명확성, 차별화 포인트, 직무 연관성 등을 평가합니다.
    """
    logger.info(
        "Introduction review request received",
        extra={"resume_id": str(resume_id), "position": request.profile.position},
    )

    response = await service.review_introduction(resume_id, request)

    logger.info(
        "Introduction review request completed", extra={"resume_id": str(resume_id)}
    )

    return response


@router.post(
    "/skills",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="스킬 리뷰",
    description="기술 스택을 평가하고 추가/제거할 기술을 제안합니다.",
)
async def review_skills(
    resume_id: UUID,
    request: ResumeSkillReviewRequest,
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    """스킬 리뷰.

    기술 스택 구성, 깊이 vs 넓이, 최신 트렌드 반영 등을 평가합니다.
    """
    logger.info("Skill review request received", extra={"resume_id": str(resume_id)})

    response = await service.review_skill(resume_id, request)

    logger.info("Skill review request completed", extra={"resume_id": str(resume_id)})

    return response


@router.post(
    "/summary",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="전체 이력서 요약 리뷰",
    description="이력서 전체를 종합적으로 평가하고 개선 방향을 제시합니다.",
)
async def review_resume_summary(
    resume_id: UUID,
    request: ResumeReviewRequest,
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    """전체 이력서 요약 리뷰.

    이력서의 전체 구성, 일관성, 차별화 포인트 등을 종합 평가합니다.
    """
    logger.info(
        "Full resume review request received",
        extra={"resume_id": str(resume_id), "section_count": len(request.sections)},
    )

    response = await service.review_summary(resume_id, request)

    logger.info("Full resume review request completed", extra={"resume_id": str(resume_id)})

    return response

@router.post(
    "/{section_type}/block",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="블록 리뷰",
    description="특정 블록(경력/프로젝트/교육 항목 하나)을 평가합니다.",
)
async def review_block(
    resume_id: UUID,
    section_type: SectionType,
    request: ResumeBlockReviewRequest,
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    """블록 리뷰.

    섹션 내 특정 블록 하나만 선택하여 상세 평가합니다.
    예: 여러 프로젝트 중 하나의 프로젝트만 리뷰
    """
    logger.info(
        "Block review request received",
        extra={
            "resume_id": str(resume_id),
            "section_type": section_type.value,
            "section_id": str(request.section_id),
            "block_id": str(request.id),
        },
    )

    response = await service.review_block(
        resume_id, section_type, request.section_id, request.id, request
    )

    logger.info(
        "Block review request completed",
        extra={"resume_id": str(resume_id), "block_id": str(request.id)},
    )

    return response


@router.post(
    "/{section_type}",
    response_model=SectionReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="섹션 리뷰",
    description="특정 섹션(경력/프로젝트/교육)의 모든 블록을 평가합니다.",
)
async def review_section(
    resume_id: UUID,
    section_type: SectionType,
    request: ResumeSectionReviewRequest,
    service: ReviewService = Depends(get_review_service),
) -> SectionReviewResponse:
    """섹션 리뷰.

    섹션 내 모든 블록을 순회하며 개별 평가 후 종합 결과를 반환합니다.

    - **work_experience**: STAR 기법 기반 경력 평가
    - **project**: 기술적 깊이 및 비즈니스 임팩트 평가
    - **education**: 직무 연관성 및 학습 성과 평가
    """
    logger.info(
        "Section review request received",
        extra={
            "resume_id": str(resume_id),
            "section_type": section_type.value,
            "section_id": str(request.id),
            "block_count": len(request.blocks),
        },
    )

    response = await service.review_section(resume_id, section_type, request)

    logger.info(
        "Section review request completed",
        extra={"resume_id": str(resume_id), "section_type": section_type.value},
    )

    return response
