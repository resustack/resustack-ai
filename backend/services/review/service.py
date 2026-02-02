from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING
from uuid import UUID

from backend.ai.output.review_result import ReviewResult, SectionReviewResult
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

logger = logging.getLogger(__name__)


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
        start_time = time.time()

        logger.info(
            "Starting full resume review",
            extra={
                "resume_id": str(resume_id),
                "operation": "review_summary",
                "section_count": len(request.sections),
            },
        )

        try:
            context = self._assembler.assemble_full(resume_id, request)
            result = await self._chain.run(context)
            response = self._mapper.to_review_response(resume_id, result)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "Full resume review completed",
                extra={
                    "resume_id": str(resume_id),
                    "operation": "review_summary",
                    "duration_ms": duration_ms,
                },
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Full resume review failed: {e}",
                extra={
                    "resume_id": str(resume_id),
                    "operation": "review_summary",
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    async def review_introduction(
        self,
        resume_id: UUID,
        request: ResumeReviewRequest,
    ) -> ReviewResponse:
        """소개글 리뷰."""
        start_time = time.time()

        logger.info(
            "Starting introduction review",
            extra={
                "resume_id": str(resume_id),
                "operation": "review_introduction",
                "position": request.profile.position,
            },
        )

        try:
            context = self._assembler.assemble_introduction(resume_id, request)
            result = await self._chain.run(context)
            response = self._mapper.to_review_response(resume_id, result)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "Introduction review completed",
                extra={
                    "resume_id": str(resume_id),
                    "operation": "review_introduction",
                    "duration_ms": duration_ms,
                },
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Introduction review failed: {e}",
                extra={
                    "resume_id": str(resume_id),
                    "operation": "review_introduction",
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    async def review_skill(
        self,
        resume_id: UUID,
        request: ResumeSkillReviewRequest,
    ) -> ReviewResponse:
        """스킬 리뷰."""
        start_time = time.time()

        # Count total skills for logging
        skill_count = sum(
            [
                len(request.skills.language),
                len(request.skills.framework),
                len(request.skills.database),
                len(request.skills.dev_ops),
                len(request.skills.tools),
                len(request.skills.library),
                len(request.skills.testing),
                len(request.skills.collaboration),
            ]
        )

        logger.info(
            "Starting skill review",
            extra={
                "resume_id": str(resume_id),
                "operation": "review_skill",
                "total_skills": skill_count,
            },
        )

        try:
            context = self._assembler.assemble_skill(resume_id, request)
            result = await self._chain.run(context)
            response = self._mapper.to_review_response(resume_id, result)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "Skill review completed",
                extra={
                    "resume_id": str(resume_id),
                    "operation": "review_skill",
                    "duration_ms": duration_ms,
                },
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Skill review failed: {e}",
                extra={
                    "resume_id": str(resume_id),
                    "operation": "review_skill",
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    async def review_section(
        self,
        resume_id: UUID,
        section_type: SectionType,
        request: ResumeSectionReviewRequest,
    ) -> SectionReviewResponse:
        """섹션 리뷰 (경력/프로젝트/교육)."""
        start_time = time.time()
        block_count = len(request.blocks)

        logger.info(
            "Starting section review",
            extra={
                "resume_id": str(resume_id),
                "operation": "review_section",
                "section_type": section_type.value,
                "section_id": str(request.id),
                "block_count": block_count,
            },
        )

        try:
            context = self._assembler.assemble_section(resume_id, section_type, request)
            block_results = await self._section_chain.run(context)
            overall_evaluation = self._summarize_block_results(block_results)

            section_result = SectionReviewResult(
                target_type=ReviewTargetType.from_section_type(section_type),
                section_id=request.id,
                overall_evaluation=overall_evaluation,
                block_results=block_results,
            )
            response = self._mapper.to_section_review_response(resume_id, section_result)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "Section review completed",
                extra={
                    "resume_id": str(resume_id),
                    "operation": "review_section",
                    "section_type": section_type.value,
                    "block_count": block_count,
                    "duration_ms": duration_ms,
                },
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Section review failed: {e}",
                extra={
                    "resume_id": str(resume_id),
                    "operation": "review_section",
                    "section_type": section_type.value,
                    "block_count": block_count,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    async def review_block(
        self,
        resume_id: UUID,
        section_type: SectionType,
        section_id: UUID,
        block_id: UUID,
        request: ResumeBlockReviewRequest,
    ) -> ReviewResponse:
        """단일 블록 리뷰."""
        start_time = time.time()

        logger.info(
            "Starting block review",
            extra={
                "resume_id": str(resume_id),
                "operation": "review_block",
                "section_type": section_type.value,
                "section_id": str(section_id),
                "block_id": str(block_id),
            },
        )

        try:
            context = self._assembler.assemble_block(
                resume_id, section_type, section_id, block_id, request
            )
            result = await self._chain.run(context)
            response = self._mapper.to_review_response(resume_id, result)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "Block review completed",
                extra={
                    "resume_id": str(resume_id),
                    "operation": "review_block",
                    "section_type": section_type.value,
                    "block_id": str(block_id),
                    "duration_ms": duration_ms,
                },
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Block review failed: {e}",
                extra={
                    "resume_id": str(resume_id),
                    "operation": "review_block",
                    "section_type": section_type.value,
                    "block_id": str(block_id),
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    def _summarize_block_results(self, results: list[ReviewResult]) -> str:
        """블록별 결과를 종합하여 섹션 전체 평가 요약 생성."""
        if not results:
            logger.warning("No block results to summarize")
            return "평가할 블록이 없습니다."

        logger.debug("Summarizing block results", extra={"result_count": len(results)})

        summaries = []
        for i, result in enumerate(results, 1):
            summary = f"{i}. {result.evaluation_summary}"
            summaries.append(summary)

        return "\n".join(summaries)
