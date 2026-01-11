from backend.ai.strategies.base import BasePromptStrategy
from backend.services.review.context import ReviewContext
from backend.utils.yaml_loader import get_prompt


class IntroductionPromptStrategy(BasePromptStrategy):
    """소개글 리뷰 프롬프트 전략."""

    def __init__(self):
        super().__init__()
        self._specific_instructions = get_prompt("introduction", "specific_instructions")
        self._evaluation_instructions = get_prompt("introduction", "evaluation_instructions")
        self._improvement_instructions = get_prompt("introduction", "improvement_instructions")

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
        intro = context.introduction
        if intro is None:
            raise ValueError("Introduction data is required")

        return f"""
**입력 정보**
- 이름: {intro.name}
- 목표 직무: {intro.position}
- 경력 요약: {intro.work_experience_summary}
- 프로젝트 요약: {intro.project_summary}

**평가 대상 - 현재 소개글**:
{intro.content}

위 소개글을 평가해주세요.
"""
