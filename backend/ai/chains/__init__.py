from functools import lru_cache

from backend.ai.chains.review_chain import ReviewChain, SectionReviewChain


@lru_cache
def get_review_chain() -> ReviewChain:
    """ReviewChain 싱글톤 인스턴스 반환."""
    return ReviewChain()

@lru_cache
def get_review_section_chain() -> SectionReviewChain:
    """SectionReviewChain 싱글톤 인스턴스 반환."""
    return SectionReviewChain()


__all__ = ["get_review_chain", "get_review_section_chain"]
