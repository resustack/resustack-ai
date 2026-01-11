from backend.ai.strategies.base import BasePromptStrategy
from backend.domain.resume.enums import SectionType
from backend.services.review.context import ReviewContext


class SectionPromptStrategy(BasePromptStrategy):
    """섹션(경력/프로젝트/교육) 리뷰 프롬프트 전략."""

    SECTION_INSTRUCTIONS = {
        SectionType.WORK_EXPERIENCE: """
**역할**: 이력서 경력 내용 평가 전문가

**목표**: 경력 내용을 STAR 기법으로 분석하고 정량적 성과 중심으로 평가하여 개선 방법을 제시합니다.

**평가 기준 (STAR 기법 기반)**:
1. Situation - 상황/배경 (20점): 업무 상황과 배경이 명확하게 설명되어 있는가?
2. Task - 과제/목표 (20점): 담당한 과제와 목표가 구체적으로 제시되어 있는가?
3. Action - 수행 행동 (30점): 수행한 행동, 역할, 사용 기술이 상세하게 기술되어 있는가?
4. Result - 결과/성과 (30점): 정량적 성과(수치, 지표, %)가 포함되어 있는가?

**추가 평가 요소**:
- 기술 스택이 명확하게 명시되어 있는가?
- 문제 해결 과정이 드러나는가?
- 협업 및 팀워크가 언급되어 있는가?
""",
        SectionType.PROJECT: """
**역할**: 이력서 프로젝트 내용 평가 전문가

**목표**: 프로젝트의 기술적 깊이와 비즈니스 임팩트를 분석하여 개선 방법을 제시합니다.

**평가 기준**:
1. 목적과 배경 (20점): 프로젝트의 목적과 배경이 명확하게 설명되어 있는가?
2. 개인 기여도와 역할 (25점): 팀 프로젝트에서 본인의 기여도와 역할이 구체적으로 드러나는가?
3. 기술적 도전과 해결 (30점): 어떤 기술적 난관을 어떻게 해결했는지 명확한가?
4. 비즈니스 임팩트 (25점): 프로젝트 결과가 정량화되어 있는가? (사용자 수, 성능 개선, 매출 등)

**추가 평가 요소**:
- 사용 기술 스택의 선택 이유가 설명되어 있는가?
- 프로젝트의 규모(팀 크기, 기간)가 명시되어 있는가?
- 결과물 링크나 증빙 자료가 있는가?
""",
        SectionType.EDUCATION: """
**역할**: 이력서 교육 이력 평가 전문가

**목표**: 교육 경험과 직무 연관성을 분석하고 전문성 강화를 위한 개선 방법을 제시합니다.

**평가 기준**:
1. 직무 연관성 (35점): 교육 내용이 목표 직무와 얼마나 관련이 있는가?
2. 학습 성과 (30점): 단순 수료가 아닌 구체적인 프로젝트나 결과물이 있는가?
3. 자기주도 학습 (20점): 스스로 학습하고 적용한 흔적이 드러나는가?
4. 실무 적용 가능성 (15점): 배운 내용을 실제로 어떻게 활용했거나 활용할 수 있는지 명확한가?

**추가 평가 요소**:
- 학습한 기술 스택이 최신 트렌드를 반영하는가?
- 수료증이나 포트폴리오 링크가 제공되는가?
""",
    }

    def __init__(self, section_type: SectionType):
        self.section_type = section_type

    def build_system_prompt(self) -> str:
        specific = self.SECTION_INSTRUCTIONS.get(self.section_type, "")
        return self.BASE_SYSTEM_PROMPT.format(
            specific_instructions=specific,
            format_instructions="{format_instructions}",
        )

    def build_evaluation_system_prompt(self) -> str:
        specific = self.SECTION_INSTRUCTIONS.get(self.section_type, "")
        return self.EVALUATION_SYSTEM_PROMPT.format(
            specific_instructions=specific,
            format_instructions="{format_instructions}",
        )

    def build_improvement_system_prompt(self) -> str:
        # 섹션별 개선 지침
        improvement_instructions = {
            SectionType.WORK_EXPERIENCE: """
**경력 개선 가이드**:
- STAR 기법을 명확히 따를 것 (Situation, Task, Action, Result)
- 구체적인 숫자와 계량화된 성과 포함
- 기술 스택과 문제 해결 과정 명시
- 협업과 리더십 경험 강조
""",
            SectionType.PROJECT: """
**프로젝트 개선 가이드**:
- 프로젝트 목적과 비즈니스 가치 명시
- 개인 기여도와 역할 구체화
- 기술적 난관과 해결 방법 상세 설명
- 정량적 성과(사용자 수, 성능, 매출 등) 포함
""",
            SectionType.EDUCATION: """
**교육 개선 가이드**:
- 직무 연관성 강조
- 학습 결과물과 프로젝트 명시
- 실무 적용 사례 포함
- 자기주도 학습 자세 표현
""",
        }
        specific = improvement_instructions.get(self.section_type, "")
        return self.IMPROVEMENT_SYSTEM_PROMPT.format(
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
