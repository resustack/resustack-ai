from backend.ai.strategies.base import BasePromptStrategy
from backend.services.review.context import ReviewContext


class SkillPromptStrategy(BasePromptStrategy):
    """스킬 리뷰 프롬프트 전략."""

    SPECIFIC_INSTRUCTIONS = """
**역할**: 이력서 기술 스택 평가 전문가

**목표**: 지원자의 기술 스택 구성을 분석하고 직무 적합성을 평가합니다.

**평가 기준**:
1. 기술 스택 구성 (30점): 언어, 프레임워크, DB 등이 균형있게 구성되어 있는가?
2. 기술 깊이 vs 넓이 (25점): 전문 분야가 명확하면서도 범용성이 있는가?
3. 최신 트렌드 반영 (25점): 현재 시장에서 수요가 높은 기술이 포함되어 있는가?
4. 일관성 (20점): 기술 스택이 목표 직무와 일관성이 있는가?
"""

    EVALUATION_INSTRUCTIONS = SPECIFIC_INSTRUCTIONS

    IMPROVEMENT_INSTRUCTIONS = """
**역할**: 기술 스택 개선 전문가

**목표**: 평가 결과를 바탕으로 최적화된 기술 스택을 제시합니다.

**개선 원칙**:
1. 직무 역량과 직접 관련된 기술을 우선하세요.
2. 현재 수요가 높고 트렌드에 맞는 기술을 추가하세요.
3. 중복되거나 오래된 기술은 제거하세요.
4. 전문성과 범용성의 균형을 맞추세요.
5. 기술 스택을 카테고리별로 정리하세요.
"""

    def build_system_prompt(self) -> str:
        return self.BASE_SYSTEM_PROMPT.format(
            specific_instructions=self.SPECIFIC_INSTRUCTIONS,
            format_instructions="{format_instructions}",
        )

    def build_evaluation_system_prompt(self) -> str:
        return self.EVALUATION_SYSTEM_PROMPT.format(
            specific_instructions=self.EVALUATION_INSTRUCTIONS,
            format_instructions="{format_instructions}",
        )

    def build_improvement_system_prompt(self) -> str:
        return self.IMPROVEMENT_SYSTEM_PROMPT.format(
            specific_instructions=self.IMPROVEMENT_INSTRUCTIONS,
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
