from abc import ABC, abstractmethod

from backend.ai.output.review_result import EvaluationResult
from backend.services.review.context import ReviewContext


class PromptStrategy(ABC):
    """프롬프트 생성 전략 인터페이스."""

    @abstractmethod
    def build_system_prompt(self) -> str:
        """시스템 프롬프트 생성 (레거시, 호환용)."""
        ...

    @abstractmethod
    def build_user_prompt(self, context: ReviewContext) -> str:
        """사용자 프롬프트 생성."""
        ...

    @abstractmethod
    def build_evaluation_system_prompt(self) -> str:
        """1단계: 평가 전용 시스템 프롬프트 생성."""
        ...

    @abstractmethod
    def build_improvement_system_prompt(self) -> str:
        """2단계: 개선 전용 시스템 프롬프트 생성."""
        ...

    @abstractmethod
    def build_improvement_user_prompt(
        self,
        context: ReviewContext,
        evaluation: EvaluationResult
    ) -> str:
        """2단계: 평가 결과를 포함한 개선 요청 프롬프트 생성."""
        ...


class BasePromptStrategy(PromptStrategy):
    """공통 프롬프트 템플릿."""

    BASE_SYSTEM_PROMPT = """당신은 전문 이력서 컨설턴트입니다.
한국 IT 업계의 채용 트렌드와 기술 스택을 깊이 이해하고 있으며,
지원자의 이력서를 평가하고 개선 방법을 제시하는 전문가입니다.

평가 시 다음 사항을 준수하세요:
1. 객관적이고 건설적인 피드백을 제공하세요.
2. 구체적인 개선 방안을 제시하세요.
3. 강점과 약점을 균형있게 평가하세요.
4. 채용 담당자 관점에서 평가하세요.

{specific_instructions}

{format_instructions}"""

    EVALUATION_SYSTEM_PROMPT = """당신은 전문 이력서 평가자입니다.
한국 IT 업계의 채용 트렌드와 기술 스택을 깊이 이해하고 있으며,
지원자의 이력서 내용을 객관적으로 평가하는 전문가입니다.

**중요: 이 단계에서는 평가만 수행하세요. 개선안은 제시하지 마세요.**

평가 시 다음 사항을 준수하세요:
1. 내용의 명확성, 구체성, 임팩트를 평가하세요.
2. 강점과 약점을 객관적으로 나열하세요.
3. 채용 담당자가 궁금해할 내용이 충분한지 평가하세요.
4. 기술적 깊이와 비즈니스 임팩트를 함께 고려하세요.

{specific_instructions}

{format_instructions}"""

    IMPROVEMENT_SYSTEM_PROMPT = """당신은 전문 이력서 개선 컨설턴트입니다.
평가 결과를 바탕으로 구체적인 개선안을 제시하는 전문가입니다.

**중요: 제공된 평가 결과를 기반으로 개선안을 작성하세요.**

개선안 작성 시 다음 사항을 준수하세요:
1. 평가에서 지적된 약점을 구체적으로 개선하세요.
2. 강점은 유지하면서 더 명확하게 표현하세요.
3. 채용 담당자가 이해하기 쉽게 작성하세요.
4. 구체적인 숫자, 기술, 성과를 포함하세요.
5. 원본의 의도와 사실은 유지하되, 표현을 개선하세요.

{specific_instructions}

{format_instructions}"""

    def build_evaluation_system_prompt(self) -> str:
        """1단계: 평가 전용 시스템 프롬프트."""
        return self.EVALUATION_SYSTEM_PROMPT

    def build_improvement_system_prompt(self) -> str:
        """2단계: 개선 전용 시스템 프롬프트."""
        return self.IMPROVEMENT_SYSTEM_PROMPT

    def build_improvement_user_prompt(
        self,
        context: ReviewContext,
        evaluation
    ) -> str:
        """2단계: 평가 결과를 포함한 개선 요청 프롬프트.

        Args:
            context: 리뷰 컨텍스트
            evaluation: 1단계 평가 결과 (EvaluationResult)
        """
        # 기본 사용자 프롬프트
        base_prompt = self.build_user_prompt(context)

        # 평가 결과 추가
        evaluation_context = f"""

## 이전 평가 결과

### 평가 요약
{evaluation.summary}

### 강점
{self._format_list(evaluation.strengths)}

### 약점
{self._format_weaknesses(evaluation.weaknesses)}

---

위 평가를 바탕으로 구체적인 개선안을 제시하세요.
"""

        return base_prompt + evaluation_context

    def _format_list(self, items: list[str]) -> str:
        """리스트를 bullet point로 포맷팅."""
        if not items:
            return "- 없음"
        return "\n".join(f"- {item}" for item in items)

    def _format_weaknesses(self, weaknesses: list) -> str:
        """약점 리스트를 포맷팅."""
        if not weaknesses:
            return "- 없음"
        result = []
        for w in weaknesses:
            result.append(f"- **문제**: {w.problem}")
            result.append(f"  **이유**: {w.reason}")
        return "\n".join(result)
