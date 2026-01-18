from backend.ai.strategies.base import BasePromptStrategy
from backend.services.review.context import ReviewContext


class FullResumePromptStrategy(BasePromptStrategy):
    """전체 이력서 리뷰 프롬프트 전략.

    full_resume.yaml의 템플릿을 사용합니다.
    """

    def get_template_name(self) -> str:
        """full_resume.yaml 템플릿 사용."""
        return "full_resume"

    def build_prompt_variables(self, context: ReviewContext) -> dict:
        """프롬프트 변수 딕셔너리 생성."""
        if context.full_resume_text is None:
            raise ValueError("Full resume text is required")

        return {
            "full_resume_text": context.full_resume_text,
        }
