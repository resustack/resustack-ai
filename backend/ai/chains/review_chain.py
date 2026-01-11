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
        """2단계 리뷰 실행: 평가 → 개선.

        Args:
            context: 리뷰 컨텍스트

        Returns:
            ReviewResult: 최종 리뷰 결과 (평가 + 개선)
        """
        # Step 1: 평가
        evaluation = await self._evaluate(context)

        # Step 2: 평가 결과를 바탕으로 개선
        improvement = await self._improve(context, evaluation)

        return improvement

    def run_sync(self, context: ReviewContext) -> ReviewResult:
        """2단계 리뷰 동기 실행 (테스트용)."""
        # Step 1: 평가
        evaluation = self._evaluate_sync(context)

        # Step 2: 평가 결과를 바탕으로 개선
        improvement = self._improve_sync(context, evaluation)

        return improvement

    async def _evaluate(self, context: ReviewContext) -> EvaluationResult:
        """1단계: 평가만 수행."""
        strategy = PromptStrategyFactory.get(context)

        evaluation_prompt = self._build_evaluation_prompt(strategy, context)
        chain = evaluation_prompt | self._llm | self._evaluation_parser

        result: EvaluationResult = await chain.ainvoke({})
        result.target_type = context.target_type

        if context.block:
            result.block_id = context.block.block_id

        return result

    def _evaluate_sync(self, context: ReviewContext) -> EvaluationResult:
        """1단계: 평가만 수행 (동기)."""
        strategy = PromptStrategyFactory.get(context)

        evaluation_prompt = self._build_evaluation_prompt(strategy, context)
        chain = evaluation_prompt | self._llm | self._evaluation_parser

        result: EvaluationResult = chain.invoke({})
        result.target_type = context.target_type

        if context.block:
            result.block_id = context.block.block_id

        return result

    async def _improve(
        self, context: ReviewContext, evaluation: EvaluationResult
    ) -> ReviewResult:
        """2단계: 평가 결과를 바탕으로 개선안 생성."""
        strategy = PromptStrategyFactory.get(context)

        improvement_prompt = self._build_improvement_prompt(
            strategy, context, evaluation
        )
        chain = improvement_prompt | self._llm | self._improvement_parser

        result: ReviewResult = await chain.ainvoke({})

        # 평가 결과를 최종 결과에 포함
        result.target_type = context.target_type
        result.strengths = evaluation.strengths
        result.weaknesses = evaluation.weaknesses
        result.evaluation_summary = evaluation.summary

        if context.block:
            result.block_id = context.block.block_id

        return result

    def _improve_sync(
        self, context: ReviewContext, evaluation: EvaluationResult
    ) -> ReviewResult:
        """2단계: 평가 결과를 바탕으로 개선안 생성 (동기)."""
        strategy = PromptStrategyFactory.get(context)

        improvement_prompt = self._build_improvement_prompt(
            strategy, context, evaluation
        )
        chain = improvement_prompt | self._llm | self._improvement_parser

        result: ReviewResult = chain.invoke({})

        # 평가 결과를 최종 결과에 포함
        result.target_type = context.target_type
        result.strengths = evaluation.strengths
        result.weaknesses = evaluation.weaknesses
        result.evaluation_summary = evaluation.summary

        if context.block:
            result.block_id = context.block.block_id

        return result

    def _build_evaluation_prompt(
        self,
        strategy: PromptStrategy,
        context: ReviewContext,
    ) -> ChatPromptTemplate:
        """평가 전용 프롬프트 생성."""
        system_prompt = strategy.build_evaluation_system_prompt()
        user_prompt = strategy.build_user_prompt(context)

        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
        ).partial(format_instructions=self._evaluation_parser.get_format_instructions())

    def _build_improvement_prompt(
        self,
        strategy: PromptStrategy,
        context: ReviewContext,
        evaluation: EvaluationResult,
    ) -> ChatPromptTemplate:
        """개선 전용 프롬프트 생성 (평가 결과 포함)."""
        system_prompt = strategy.build_improvement_system_prompt()

        # 평가 결과를 개선 프롬프트에 주입
        user_prompt = strategy.build_improvement_user_prompt(context, evaluation)

        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
        ).partial(format_instructions=self._improvement_parser.get_format_instructions())


class SectionReviewChain:
    """섹션 리뷰 체인 - 여러 블록을 순차 처리."""

    def __init__(self):
        self._single_chain = ReviewChain()

    async def run(self, context: ReviewContext) -> list[ReviewResult]:
        """섹션 내 모든 블록 리뷰."""
        if context.section is None:
            raise ValueError("Section data is required")

        results = []
        for block in context.section.blocks:
            block_context = ReviewContext(
                resume_id=context.resume_id,
                target_type=self._get_block_target_type(context.target_type),
                section=context.section,
                block=block,
            )
            result = await self._single_chain.run(block_context)
            results.append(result)

        return results

    def _get_block_target_type(
        self,
        section_target_type: ReviewTargetType,
    ) -> ReviewTargetType:
        """섹션 타입에서 블록 타입으로 변환."""
        mapping = {
            ReviewTargetType.WORK_EXPERIENCE: ReviewTargetType.WORK_EXPERIENCE_BLOCK,
            ReviewTargetType.PROJECT: ReviewTargetType.PROJECT_BLOCK,
            ReviewTargetType.EDUCATION: ReviewTargetType.EDUCATION_BLOCK,
        }
        return mapping.get(section_target_type, section_target_type)
