from backend.ai.strategies.base import BasePromptStrategy
from backend.domain.resume.enums import SectionType
from backend.services.review.context import ReviewContext


class SectionPromptStrategy(BasePromptStrategy):
    """섹션(경력/프로젝트/교육) 리뷰 프롬프트 전략."""

    # SectionType을 YAML 키로 매핑
    _SECTION_TYPE_TO_KEY = {
        SectionType.WORK_EXPERIENCE: "work_experience",
        SectionType.PROJECT: "project",
        SectionType.EDUCATION: "education",
    }

    def __init__(self, section_type: SectionType):
        self.section_type = section_type
        self._section_key = self._SECTION_TYPE_TO_KEY.get(section_type, "work_experience")
        super().__init__()

    def get_template_name(self) -> str:
        """사용할 YAML 템플릿 이름 반환."""
        return "section"

    def _get_specific_instructions(self, key: str = "evaluation_instructions") -> str:
        """섹션별 세부 지침 반환 (섹션 타입에 따라 다른 지침 사용)."""
        template = self._get_template()
        section_config = template.get(self._section_key, {})

        # improvement_instructions는 해당 키로, evaluation은 specific_instructions 사용
        if key == "improvement_instructions":
            return section_config.get("improvement_instructions", "")
        return section_config.get("specific_instructions", "")

    def build_prompt_variables(self, context: ReviewContext) -> dict:
        """프롬프트 변수 딕셔너리 생성."""
        section = context.section
        if section is None:
            raise ValueError("Section data is required")

        blocks_text = self._format_blocks(section.blocks)

        return {
            "section_title": section.title,
            "blocks_text": blocks_text,
        }

    def _format_blocks(self, blocks: list) -> str:
        """블록 리스트를 포맷팅."""
        blocks_text = []
        for i, block in enumerate(blocks, 1):
            block_text = f"""
### 블록 {i}: {block.sub_title}
- 기간: {block.period}
- 기술 스택: {", ".join(block.tech_stack) if block.tech_stack else "없음"}
- 링크: {block.link or "없음"}
- 내용:
{block.content}
"""
            blocks_text.append(block_text)
        return "\n".join(blocks_text)
