import asyncio
import logging

from anthropic import AnthropicError
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from backend.ai.chains.llm import get_anthropic_client
from backend.ai.output.review_result import EvaluationResult, ReviewResult
from backend.ai.strategies.base import PromptStrategy
from backend.ai.strategies.factory import PromptStrategyFactory
from backend.api.rest.exceptions import ReviewServiceError
from backend.services.review.context import ReviewContext
from backend.services.review.enums import ReviewTargetType

logger = logging.getLogger(__name__)


class ReviewChain:
    """2단계 리뷰 체인: 평가 → 개선.

    1단계: 내용을 평가하여 강점과 약점을 파악합니다.
    2단계: 평가 결과를 바탕으로 구체적인 개선안을 생성합니다.
    """

    def __init__(self):
        self._llm = get_anthropic_client()
        self._evaluation_parser = PydanticOutputParser(pydantic_object=EvaluationResult)
        self._improvement_parser = PydanticOutputParser(pydantic_object=ReviewResult)

    async def run(self, context: ReviewContext) -> ReviewResult:
        """2단계 리뷰 실행: 평가 → 개선."""
        strategy = PromptStrategyFactory.get(context)

        try:
            # Step 1: 평가
            evaluation = await self._evaluate(strategy, context)

            # Step 2: 평가 결과를 바탕으로 개선
            return await self._improve(strategy, context, evaluation)

        except AnthropicError as e:
            logger.error(
                f"Anthropic API 에러 발생: {e}",
                extra={
                    "error_type": type(e).__name__,
                    "target_type": context.target_type,
                    "resume_id": context.resume_id,
                },
                exc_info=True,
            )
            raise ReviewServiceError(
                "AI 서비스 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            ) from e

        except OutputParserException as e:
            logger.error(
                f"AI 응답 파싱 실패: {e}",
                extra={
                    "llm_output": e.llm_output[:500] if e.llm_output else None,
                    "target_type": context.target_type,
                    "resume_id": context.resume_id,
                },
                exc_info=True,
            )
            raise ReviewServiceError("AI 응답 형식이 올바르지 않습니다. 다시 시도해주세요.") from e

        except Exception as e:
            logger.error(
                f"예상치 못한 에러 발생: {e}",
                extra={
                    "error_type": type(e).__name__,
                    "target_type": context.target_type,
                    "resume_id": context.resume_id,
                },
                exc_info=True,
            )
            raise ReviewServiceError("서비스 처리 중 오류가 발생했습니다.") from e

    async def _evaluate(self, strategy: PromptStrategy, context: ReviewContext) -> EvaluationResult:
        """1단계: 평가만 수행."""
        logger.info(
            f"평가 시작: target_type={context.target_type}",
            extra={"resume_id": context.resume_id},
        )

        # 프롬프트 생성
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", strategy.build_evaluation_system_prompt()),
                ("human", strategy.get_user_prompt_template()),
            ]
        ).partial(format_instructions=self._evaluation_parser.get_format_instructions())

        # 체인 실행 (with_retry가 적용된 LLM 사용)
        chain = prompt | self._llm | self._evaluation_parser
        result: EvaluationResult = await chain.ainvoke(strategy.build_prompt_variables(context))

        logger.info(
            f"평가 완료: target_type={context.target_type}",
            extra={"resume_id": context.resume_id},
        )

        # 메타데이터 설정
        result.target_type = context.target_type
        if context.block:
            result.block_id = context.block.block_id

        return result

    async def _improve(
        self, strategy: PromptStrategy, context: ReviewContext, evaluation: EvaluationResult
    ) -> ReviewResult:
        """2단계: 평가 결과를 바탕으로 개선안 생성."""
        logger.info(
            f"개선 시작: target_type={context.target_type}",
            extra={"resume_id": context.resume_id},
        )

        # 프롬프트 생성
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", strategy.build_improvement_system_prompt()),
                ("human", strategy.get_improvement_prompt_template()),
            ]
        ).partial(format_instructions=self._improvement_parser.get_format_instructions())

        chain = prompt | self._llm | self._improvement_parser
        result: ReviewResult = await chain.ainvoke(
            strategy.build_improvement_variables(context, evaluation)
        )

        logger.info(
            f"개선 완료: target_type={context.target_type}",
            extra={"resume_id": context.resume_id},
        )

        # 평가 결과를 최종 결과에 포함
        result.target_type = context.target_type
        result.strengths = evaluation.strengths
        result.weaknesses = evaluation.weaknesses
        result.evaluation_summary = evaluation.summary
        if context.block:
            result.block_id = context.block.block_id

        return result


class SectionReviewChain:
    """섹션 리뷰 체인 - 여러 블록을 순차 처리."""

    def __init__(self):
        self._single_chain = ReviewChain()

    async def run(self, context: ReviewContext) -> list[ReviewResult]:
        """섹션 내 모든 블록을 병렬로 리뷰."""
        if context.section is None:
            raise ValueError("Section data is required")

        block_target_type = ReviewTargetType.from_section_type_block(context.section.section_type)

        # 모든 블록 컨텍스트 생성
        block_contexts = [
            ReviewContext(
                resume_id=context.resume_id,
                target_type=block_target_type,
                section=context.section,
                block=block,
            )
            for block in context.section.blocks
        ]

        logger.info(
            f"섹션 리뷰 시작: {len(block_contexts)}개 블록 병렬 처리",
            extra={
                "resume_id": context.resume_id,
                "section_type": context.section.section_type,
            },
        )

        try:
            results = await asyncio.gather(
                *[self._single_chain.run(ctx) for ctx in block_contexts],
                return_exceptions=False,
            )

            logger.info(
                f"섹션 리뷰 완료: {len(results)}개 블록 처리 완료",
                extra={"resume_id": context.resume_id},
            )

            return list(results)

        except Exception as e:
            logger.error(
                f"섹션 리뷰 실패: {e}",
                extra={
                    "resume_id": context.resume_id,
                    "section_type": context.section.section_type,
                    "total_blocks": len(block_contexts),
                },
                exc_info=True,
            )
            raise
