import asyncio

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from backend.ai.chains.llm import get_anthropic_client
from backend.ai.output.review_result import EvaluationResult, ReviewResult
from backend.ai.strategies.base import PromptStrategy
from backend.ai.strategies.factory import PromptStrategyFactory
from backend.services.review.context import ReviewContext
from backend.services.review.enums import ReviewTargetType


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

        # Step 1: 평가
        evaluation = await self._evaluate(strategy, context)

        # Step 2: 평가 결과를 바탕으로 개선
        return await self._improve(strategy, context, evaluation)

    async def _evaluate(
        self,
        strategy: PromptStrategy,
        context: ReviewContext
    ) -> EvaluationResult:
        """1단계: 평가만 수행."""

        # 프롬프트 생성
        prompt = ChatPromptTemplate.from_messages([
            ("system", strategy.build_evaluation_system_prompt()),
            ("human", strategy.get_user_prompt_template()),
        ]).partial(format_instructions=self._evaluation_parser.get_format_instructions())

        # 체인 실행
        chain = prompt | self._llm | self._evaluation_parser
        result: EvaluationResult = await chain.ainvoke(strategy.build_prompt_variables(context))

        # 메타데이터 설정
        result.target_type = context.target_type
        if context.block:
            result.block_id = context.block.block_id

        return result

    async def _improve(
        self,
        strategy: PromptStrategy,
        context: ReviewContext,
        evaluation: EvaluationResult
    ) -> ReviewResult:
        """2단계: 평가 결과를 바탕으로 개선안 생성."""

        # 프롬프트 생성
        prompt = ChatPromptTemplate.from_messages([
            ("system", strategy.build_improvement_system_prompt()),
            ("human", strategy.get_improvement_prompt_template()),
        ]).partial(format_instructions=self._improvement_parser.get_format_instructions())

        # 체인 실행
        chain = prompt | self._llm | self._improvement_parser
        result: ReviewResult = await chain.ainvoke(
            strategy.build_improvement_variables(context, evaluation)
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

        block_target_type = ReviewTargetType.from_section_type_block(
            context.section.section_type
        )

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

        # 병렬 실행
        results = await asyncio.gather(
            *[self._single_chain.run(ctx) for ctx in block_contexts]
        )

        return list(results)
