from fastapi import Depends

from backend.ai.chains import get_review_chain, get_review_section_chain
from backend.ai.chains.review_chain import ReviewChain, SectionReviewChain
from backend.services.review.assembler import ReviewContextAssembler, get_review_context_assembler
from backend.services.review.mapper import ReviewResponseMapper, get_review_response_mapper
from backend.services.review.service import ReviewService


def get_review_service(
    assembler: ReviewContextAssembler = Depends(get_review_context_assembler),
    chain: ReviewChain = Depends(get_review_chain),
    section_chain: SectionReviewChain = Depends(get_review_section_chain),
    mapper: ReviewResponseMapper = Depends(get_review_response_mapper),
) -> ReviewService:
    """ReviewService 인스턴스 반환 (의존성 주입)."""
    return ReviewService(
        assembler=assembler,
        chain=chain,
        section_chain=section_chain,
        mapper=mapper,
    )


__all__ = [
    "ReviewService",
    "ReviewContextAssembler",
    "ReviewContext",
    "ReviewTargetType",
    "get_review_service",
]
