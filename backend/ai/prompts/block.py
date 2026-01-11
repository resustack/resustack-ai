from backend.ai.prompts.section import SectionPromptStrategy
from backend.ai.strategies.base import BasePromptStrategy
from backend.domain.resume.enums import SectionType
from backend.services.review.context import ReviewContext


class BlockPromptStrategy(BasePromptStrategy):
    """단일 블록 리뷰 프롬프트 전략."""

    def __init__(self, section_type: SectionType):
        self.section_type = section_type
        self._section_strategy = SectionPromptStrategy(section_type)

    def build_system_prompt(self) -> str:
        return self._section_strategy.build_system_prompt()

    def build_evaluation_system_prompt(self) -> str:
        return self._section_strategy.build_evaluation_system_prompt()

    def build_improvement_system_prompt(self) -> str:
        return self._section_strategy.build_improvement_system_prompt()

    def build_user_prompt(self, context: ReviewContext) -> str:
        block = context.block
        if block is None:
            raise ValueError("Block data is required")

        section_context = ""
        if context.section:
            section_context = f"(섹션: {context.section.title})"

        return f"""
**평가 대상 - 단일 블록** {section_context}

### {block.sub_title}
- 기간: {block.period}
- 기술 스택: {', '.join(block.tech_stack) if block.tech_stack else '없음'}
- 링크: {block.link or '없음'}
- 내용:
{block.content}

위 내용을 평가해주세요.
"""
