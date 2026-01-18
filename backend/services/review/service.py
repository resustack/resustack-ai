from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from backend.api.rest.v1.schemas.resumes import (
    ResumeBlockReviewRequest,
    ResumeReviewRequest,
    ResumeSectionReviewRequest,
    ResumeSkillReviewRequest,
)
from backend.api.rest.v1.schemas.reviews import ReviewResponse, SectionReviewResponse
from backend.domain.resume.enums import SectionType
from backend.services.review.assembler import ReviewContextAssembler
from backend.services.review.enums import ReviewTargetType
from backend.services.review.mapper import ReviewResponseMapper

if TYPE_CHECKING:
    from backend.ai.chains.review_chain import ReviewChain, SectionReviewChain
    from backend.ai.output.review_result import ReviewResult, SectionReviewResult


class ReviewService:
    """리뷰 서비스."""

    def __init__(
        self,
        assembler: ReviewContextAssembler,
        chain: ReviewChain,
        section_chain: SectionReviewChain,
        mapper: ReviewResponseMapper,
    ):
        self._assembler = assembler
        self._chain = chain
        self._section_chain = section_chain
        self._mapper = mapper

    async def review_summary(
        self,
        resume_id: UUID,
        request: ResumeReviewRequest,
    ) -> ReviewResponse:
        """전체 이력서 요약 리뷰."""
        context = self._assembler.assemble_full(resume_id, request)
        result = await self._chain.run(context)
        return self._mapper.to_review_response(resume_id, result)

    async def review_introduction(
        self,
        resume_id: UUID,
        request: ResumeReviewRequest,
    ) -> ReviewResponse:
        """소개글 리뷰."""
        context = self._assembler.assemble_introduction(resume_id, request)
        result = await self._chain.run(context)
        return self._mapper.to_review_response(resume_id, result)

    async def review_skill(
        self,
        resume_id: UUID,
        request: ResumeSkillReviewRequest,
    ) -> ReviewResponse:
        """스킬 리뷰."""
        context = self._assembler.assemble_skill(resume_id, request)
        result = await self._chain.run(context)
        return self._mapper.to_review_response(resume_id, result)

    async def review_section(
        self,
        resume_id: UUID,
        section_type: SectionType,
        request: ResumeSectionReviewRequest,
    ) -> SectionReviewResponse:
        """섹션 리뷰 (경력/프로젝트/교육)."""
        context = self._assembler.assemble_section(resume_id, section_type, request)
        block_results = await self._section_chain.run(context)
        overall_evaluation = self._summarize_block_results(block_results)

        section_result = SectionReviewResult(
            target_type=ReviewTargetType.from_section_type(section_type),
            section_id=request.id,
            overall_evaluation=overall_evaluation,
            block_results=block_results,
        )
        return self._mapper.to_section_review_response(resume_id, section_result)

    async def review_block(
        self,
        resume_id: UUID,
        section_type: SectionType,
        section_id: UUID,
        block_id: UUID,
        request: ResumeBlockReviewRequest,
    ) -> ReviewResponse:
        """단일 블록 리뷰."""
        context = self._assembler.assemble_block(
            resume_id, section_type, section_id, block_id, request
        )
        result = await self._chain.run(context)
        return self._mapper.to_review_response(resume_id, result)

    def _summarize_block_results(self, results: list[ReviewResult]) -> str:
        """블록별 결과를 종합하여 섹션 전체 평가 요약 생성."""
        if not results:
            return "평가할 블록이 없습니다."

        summaries = []
        for i, result in enumerate(results, 1):
            summary = f"{i}. {result.evaluation_summary}"
            summaries.append(summary)

        return "\n".join(summaries)
