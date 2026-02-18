from typing import TYPE_CHECKING

from fastapi import Depends

from backend.services.review.assembler import ReviewContextAssembler, get_review_context_assembler
from backend.services.review.context import ReviewContext
from backend.services.review.enums import ReviewTargetType
from backend.services.review.mapper import ReviewResponseMapper, get_review_response_mapper
from backend.services.review.service import ReviewService

if TYPE_CHECKING:
    from backend.ai.chains.review_chain import ReviewChain, SectionReviewChain


def get_review_service(
    assembler: ReviewContextAssembler = Depends(get_review_context_assembler),
    chain: "ReviewChain" = Depends(lambda: _get_review_chain()),
    section_chain: "SectionReviewChain" = Depends(lambda: _get_section_chain()),
    mapper: ReviewResponseMapper = Depends(get_review_response_mapper),
) -> ReviewService:
    """ReviewService 인스턴스 반환 (의존성 주입)."""
    return ReviewService(
        assembler=assembler,
        chain=chain,
        section_chain=section_chain,
        mapper=mapper,
    )


def _get_review_chain():
    """지연 로딩으로 순환 참조 방지."""
    from backend.ai.chains import get_review_chain

    return get_review_chain()


def _get_section_chain():
    """지연 로딩으로 순환 참조 방지."""
    from backend.ai.chains import get_review_section_chain

    return get_review_section_chain()


__all__ = [
    "ReviewService",
    "ReviewContextAssembler",
    "ReviewContext",
    "ReviewTargetType",
    "get_review_service",
]
