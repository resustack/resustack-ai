from abc import ABC, abstractmethod

from backend.ai.output.review_result import EvaluationResult
from backend.services.review.context import ReviewContext
from backend.utils.yaml_loader import get_prompt


class PromptStrategy(ABC):
    """프롬프트 생성 전략 인터페이스."""

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
    """공통 프롬프트 템플릿 (YAML 기반)."""

    def __init__(self):
        # 기본 프롬프트 템플릿 로드
        self._base_system_prompt = get_prompt("base", "base_system_prompt")
        self._evaluation_system_prompt = get_prompt("base", "evaluation_system_prompt")
        self._improvement_system_prompt = get_prompt("base", "improvement_system_prompt")

    def build_evaluation_system_prompt(self) -> str:
        """1단계: 평가 전용 시스템 프롬프트."""
        return self._evaluation_system_prompt

    def build_improvement_system_prompt(self) -> str:
        """2단계: 개선 전용 시스템 프롬프트."""
        return self._improvement_system_prompt

    def build_improvement_user_prompt(
        self,
        context: ReviewContext,
        evaluation: EvaluationResult
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
{self._format_list(evaluation.weaknesses)}

---

위 평가를 바탕으로 구체적인 개선안을 제시하세요.
"""

        return base_prompt + evaluation_context

    def _format_list(self, items: list[str]) -> str:
        """리스트를 bullet point로 포맷팅."""
        if not items:
            return "- 없음"
        return "\n".join(f"- {item}" for item in items)
