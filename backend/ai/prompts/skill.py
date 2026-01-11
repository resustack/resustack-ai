from backend.ai.strategies.base import BasePromptStrategy
from backend.services.review.context import ReviewContext
from backend.utils.yaml_loader import get_prompt


class SkillPromptStrategy(BasePromptStrategy):
    """스킬 리뷰 프롬프트 전략."""

    def __init__(self):
        super().__init__()
        self._specific_instructions = get_prompt("skill", "specific_instructions")
        self._evaluation_instructions = get_prompt("skill", "evaluation_instructions")
        self._improvement_instructions = get_prompt("skill", "improvement_instructions")

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
        skill = context.skill
        if skill is None:
            raise ValueError("Skill data is required")

        return f"""
**평가 대상 - 기술 스택**:
- 프로그래밍 언어: {', '.join(skill.language) if skill.language else '없음'}
- 프레임워크: {', '.join(skill.framework) if skill.framework else '없음'}
- 데이터베이스: {', '.join(skill.database) if skill.database else '없음'}
- DevOps: {', '.join(skill.dev_ops) if skill.dev_ops else '없음'}
- 도구: {', '.join(skill.tools) if skill.tools else '없음'}
- 라이브러리: {', '.join(skill.library) if skill.library else '없음'}
- 테스팅: {', '.join(skill.testing) if skill.testing else '없음'}
- 협업 도구: {', '.join(skill.collaboration) if skill.collaboration else '없음'}

위 기술 스택을 평가해주세요.
"""
