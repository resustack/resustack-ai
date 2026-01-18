from backend.ai.strategies.base import BasePromptStrategy
from backend.services.review.context import ReviewContext


class IntroductionPromptStrategy(BasePromptStrategy):
    """소개글 리뷰 프롬프트 전략."""

    def get_template_name(self) -> str:
        """사용할 YAML 템플릿 이름 반환."""
        return "introduction"

    def build_prompt_variables(self, context: ReviewContext) -> dict:
        """프롬프트 변수 딕셔너리 생성."""
        intro = context.introduction
        if intro is None:
            raise ValueError("Introduction data is required")

        return {
            "name": intro.name,
            "position": intro.position,
            "work_experience_summary": intro.work_experience_summary,
            "project_summary": intro.project_summary,
            "content": intro.content,
        }
