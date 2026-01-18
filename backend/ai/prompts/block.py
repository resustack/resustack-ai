from backend.ai.strategies.base import BasePromptStrategy
from backend.domain.resume.enums import SectionType
from backend.services.review.context import ReviewContext


class BlockPromptStrategy(BasePromptStrategy):
    """단일 블록 리뷰 프롬프트 전략.

    section.yaml의 block_user_prompt_template, block_improvement_prompt_template을 사용합니다.
    시스템 프롬프트는 SectionType에 따른 specific_instructions를 사용합니다.
    """

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
        """section.yaml 템플릿 사용 (block_* 템플릿 포함)."""
        return "section"

    def _get_specific_instructions(self, key: str = "evaluation_instructions") -> str:
        """SectionType에 따른 specific_instructions 반환."""
        template = self._get_template()
        section_config = template.get(self._section_key, {})

        # improvement_instructions는 해당 키로, evaluation은 specific_instructions 사용
        if key == "improvement_instructions":
            return section_config.get("improvement_instructions", "")
        return section_config.get("specific_instructions", "")

    def get_user_prompt_template(self) -> str:
        """블록 전용 사용자 프롬프트 템플릿 반환."""
        return self._get_template().get("block_user_prompt_template", "")

    def get_improvement_prompt_template(self) -> str:
        """블록 전용 개선 프롬프트 템플릿 반환."""
        return self._get_template().get("block_improvement_prompt_template", "")

    def build_prompt_variables(self, context: ReviewContext) -> dict:
        """프롬프트 변수 딕셔너리 생성."""
        block = context.block
        if block is None:
            raise ValueError("Block data is required")

        section_context = ""
        if context.section:
            section_context = f"(섹션: {context.section.title})"

        return {
            "section_context": section_context,
            "sub_title": block.sub_title,
            "period": block.period,
            "tech_stack": ", ".join(block.tech_stack) if block.tech_stack else "없음",
            "link": block.link or "없음",
            "content": block.content,
        }
