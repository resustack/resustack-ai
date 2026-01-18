from backend.ai.prompts.block import BlockPromptStrategy
from backend.ai.prompts.full_resume import FullResumePromptStrategy
from backend.ai.prompts.introduction import IntroductionPromptStrategy
from backend.ai.prompts.section import SectionPromptStrategy
from backend.ai.prompts.skill import SkillPromptStrategy
from backend.ai.strategies.base import PromptStrategy
from backend.domain.resume.enums import SectionType
from backend.services.review.context import ReviewContext
from backend.services.review.enums import ReviewTargetType


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
