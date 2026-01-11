from backend.ai.prompts.block import BlockPromptStrategy
from backend.ai.prompts.introduction import IntroductionPromptStrategy
from backend.ai.prompts.section import SectionPromptStrategy
from backend.ai.prompts.skill import SkillPromptStrategy
from backend.ai.strategies.base import PromptStrategy
from backend.domain.resume.enums import SectionType
from backend.services.review.context import ReviewContext
from backend.services.review.enums import ReviewTargetType


class FullResumePromptStrategy:
    """전체 이력서 리뷰 프롬프트 전략."""

    BASE_SYSTEM_PROMPT = """당신은 전문 이력서 컨설턴트입니다.
한국 IT 업계의 채용 트렌드와 기술 스택을 깊이 이해하고 있으며,
지원자의 이력서를 평가하고 개선 방법을 제시하는 전문가입니다.

평가 시 다음 사항을 준수하세요:
1. 객관적이고 건설적인 피드백을 제공하세요.
2. 구체적인 개선 방안을 제시하세요.
3. 강점과 약점을 균형있게 평가하세요.
4. 채용 담당자 관점에서 평가하세요.

{specific_instructions}

{format_instructions}"""

    SPECIFIC_INSTRUCTIONS = """
**역할**: 이력서 전체 평가 전문가

**목표**: 이력서 전체를 종합적으로 평가하고 전반적인 개선 방향을 제시합니다.

**평가 기준**:
1. 전체 구성 및 흐름 (25점): 이력서의 구성이 논리적이고 읽기 쉬운가?
2. 일관성 (25점): 프로필, 경력, 프로젝트, 스킬이 일관된 스토리를 전달하는가?
3. 차별화 포인트 (25점): 지원자만의 강점과 개성이 드러나는가?
4. 완성도 (25점): 오탈자, 형식 오류, 누락된 정보가 없는가?
"""

    def build_system_prompt(self) -> str:
        return self.BASE_SYSTEM_PROMPT.format(
            specific_instructions=self.SPECIFIC_INSTRUCTIONS,
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
