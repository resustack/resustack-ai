from backend.ai.strategies.base import BasePromptStrategy
from backend.domain.resume.enums import SectionType
from backend.services.review.context import ReviewContext
from backend.utils.yaml_loader import load_prompt_template


class SectionPromptStrategy(BasePromptStrategy):
    """섹션(경력/프로젝트/교육) 리뷰 프롬프트 전략."""

    # SectionType을 YAML 키로 매핑
    _SECTION_TYPE_TO_KEY = {
        SectionType.WORK_EXPERIENCE: "work_experience",
        SectionType.PROJECT: "project",
        SectionType.EDUCATION: "education",
    }

    def __init__(self, section_type: SectionType):
        super().__init__()
        self.section_type = section_type
        self._section_templates = load_prompt_template("section")
        self._section_key = self._SECTION_TYPE_TO_KEY.get(section_type, "")

    def _get_section_instructions(self) -> str:
        """섹션별 평가 지침 반환."""
        if self._section_key and self._section_key in self._section_templates:
            return self._section_templates[self._section_key].get("specific_instructions", "")
        return ""

    def _get_improvement_instructions(self) -> str:
        """섹션별 개선 지침 반환."""
        if self._section_key and self._section_key in self._section_templates:
            return self._section_templates[self._section_key].get("improvement_instructions", "")
        return ""

    def build_evaluation_system_prompt(self) -> str:
        specific = self._get_section_instructions()
        return self._evaluation_system_prompt.format(
            specific_instructions=specific,
            format_instructions="{format_instructions}",
        )

    def build_improvement_system_prompt(self) -> str:
        specific = self._get_improvement_instructions()
        return self._improvement_system_prompt.format(
            specific_instructions=specific,
            format_instructions="{format_instructions}",
        )

    def build_user_prompt(self, context: ReviewContext) -> str:
        section = context.section
        if section is None:
            raise ValueError("Section data is required")

        blocks_text = []
        for i, block in enumerate(section.blocks, 1):
            block_text = f"""
### 블록 {i}: {block.sub_title}
- 기간: {block.period}
- 기술 스택: {', '.join(block.tech_stack) if block.tech_stack else '없음'}
- 링크: {block.link or '없음'}
- 내용:
{block.content}
"""
            blocks_text.append(block_text)

        return f"""
**평가 대상 - {section.title} 섹션**

{chr(10).join(blocks_text)}

위 내용을 각 블록별로 평가해주세요.
"""
