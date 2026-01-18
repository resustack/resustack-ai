from backend.ai.strategies.base import BasePromptStrategy
from backend.services.review.context import ReviewContext


class SkillPromptStrategy(BasePromptStrategy):
    """스킬 리뷰 프롬프트 전략."""

    def get_template_name(self) -> str:
        """사용할 YAML 템플릿 이름 반환."""
        return "skill"

    def build_prompt_variables(self, context: ReviewContext) -> dict:
        """프롬프트 변수 딕셔너리 생성."""
        skill = context.skill
        if skill is None:
            raise ValueError("Skill data is required")

        return {
            "language": ", ".join(skill.language) if skill.language else "없음",
            "framework": ", ".join(skill.framework) if skill.framework else "없음",
            "database": ", ".join(skill.database) if skill.database else "없음",
            "dev_ops": ", ".join(skill.dev_ops) if skill.dev_ops else "없음",
            "tools": ", ".join(skill.tools) if skill.tools else "없음",
            "library": ", ".join(skill.library) if skill.library else "없음",
            "testing": ", ".join(skill.testing) if skill.testing else "없음",
            "collaboration": ", ".join(skill.collaboration) if skill.collaboration else "없음",
        }
