from backend.ai.prompts.block import BlockPromptStrategy
from backend.ai.prompts.introduction import IntroductionPromptStrategy
from backend.ai.prompts.section import SectionPromptStrategy
from backend.ai.prompts.skill import SkillPromptStrategy
from backend.ai.strategies.base import BasePromptStrategy, PromptStrategy
from backend.domain.resume.enums import SectionType
from backend.services.review.context import ReviewContext
from backend.services.review.enums import ReviewTargetType
from backend.utils.yaml_loader import get_prompt


class FullResumePromptStrategy(BasePromptStrategy):
    """전체 이력서 리뷰 프롬프트 전략."""

    def __init__(self):
        super().__init__()
        self._specific_instructions = get_prompt("full_resume", "specific_instructions")
        self._evaluation_instructions = get_prompt("full_resume", "evaluation_instructions")
        self._improvement_instructions = get_prompt("full_resume", "improvement_instructions")

    def build_evaluation_system_prompt(self) -> str:
        return self._evaluation_system_prompt.format(
            specific_instructions=self._evaluation_instructions,
            format_instructions="{format_instructions}",
        )

    def build_improvement_system_prompt(self) -> str:
        return self._improvement_system_prompt.format(
            specific_instructions=self._improvement_instructions,
            format_instructions="{format_instructions}",
        )

    def build_user_prompt(self, context: ReviewContext) -> str:
        if context.full_resume_text is None:
            raise ValueError("Full resume text is required")

        return f"""
**평가 대상 - 전체 이력서**

{context.full_resume_text}

위 이력서를 전체적으로 평가하고, 종합적인 개선 방향을 제시해주세요.
"""


class PromptStrategyFactory:
    """ReviewContext에 맞는 PromptStrategy를 반환하는 팩토리."""

    @staticmethod
    def get(context: ReviewContext) -> PromptStrategy:
        """ReviewContext.target_type에 따라 적절한 PromptStrategy 반환."""
        target_type = context.target_type

        match target_type:
            case ReviewTargetType.RESUME_FULL:
                return FullResumePromptStrategy()

            case ReviewTargetType.INTRODUCTION:
                return IntroductionPromptStrategy()

            case ReviewTargetType.SKILL:
                return SkillPromptStrategy()

            case ReviewTargetType.WORK_EXPERIENCE:
                return SectionPromptStrategy(SectionType.WORK_EXPERIENCE)

            case ReviewTargetType.PROJECT:
                return SectionPromptStrategy(SectionType.PROJECT)

            case ReviewTargetType.EDUCATION:
                return SectionPromptStrategy(SectionType.EDUCATION)

            case ReviewTargetType.WORK_EXPERIENCE_BLOCK:
                return BlockPromptStrategy(SectionType.WORK_EXPERIENCE)

            case ReviewTargetType.PROJECT_BLOCK:
                return BlockPromptStrategy(SectionType.PROJECT)

            case ReviewTargetType.EDUCATION_BLOCK:
                return BlockPromptStrategy(SectionType.EDUCATION)

            case _:
                raise ValueError(f"Unknown target type: {target_type}")
