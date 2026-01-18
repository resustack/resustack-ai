from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from backend.services.review.context import ReviewContext
from backend.utils.yaml_loader import get_prompt, load_prompt_template

if TYPE_CHECKING:
    from backend.ai.output.review_result import EvaluationResult


class PromptStrategy(ABC):
    """프롬프트 생성 전략 인터페이스.

    서브클래스는 다음 두 메서드만 구현하면 됩니다:
    - get_template_name(): 사용할 YAML 템플릿 이름
    - build_prompt_variables(): 프롬프트 변수 딕셔너리 생성
    """

    @abstractmethod
    def get_template_name(self) -> str:
        """사용할 YAML 템플릿 이름 반환 (확장자 제외)."""
        ...

    @abstractmethod
    def build_prompt_variables(self, context: ReviewContext) -> dict:
        """프롬프트 변수 딕셔너리 생성."""
        ...


class BasePromptStrategy(PromptStrategy):
    """공통 프롬프트 전략 구현 (YAML 기반 템플릿 메서드 패턴).

    서브클래스는 get_template_name()과 build_prompt_variables()만 구현하면
    시스템 프롬프트, 사용자 프롬프트, 개선 프롬프트가 자동으로 구성됩니다.
    """

    def __init__(self):
        # 기본 시스템 프롬프트 로드
        self._evaluation_system_prompt = get_prompt("base", "evaluation_system_prompt")
        self._improvement_system_prompt = get_prompt("base", "improvement_system_prompt")
        # 타입별 템플릿 (지연 로드)
        self._template: dict | None = None

    def _get_template(self) -> dict:
        """YAML 템플릿 로드 (지연 로드 + 캐싱)."""
        if self._template is None:
            self._template = load_prompt_template(self.get_template_name())
        return self._template

    def _get_specific_instructions(self, key: str = "evaluation_instructions") -> str:
        """타입별 세부 지침 반환."""
        template = self._get_template()
        # evaluation_instructions가 없으면 specific_instructions 사용
        return template.get(key, template.get("specific_instructions", ""))

    # ===== 시스템 프롬프트 (템플릿 메서드) =====

    def build_evaluation_system_prompt(self) -> str:
        """1단계: 평가 전용 시스템 프롬프트 생성."""
        return self._evaluation_system_prompt.format(
            specific_instructions=self._get_specific_instructions("evaluation_instructions"),
            format_instructions="{format_instructions}",
        )

    def build_improvement_system_prompt(self) -> str:
        """2단계: 개선 전용 시스템 프롬프트 생성."""
        return self._improvement_system_prompt.format(
            specific_instructions=self._get_specific_instructions("improvement_instructions"),
            format_instructions="{format_instructions}",
        )

    # ===== 사용자 프롬프트 템플릿 (YAML에서 로드) =====

    def get_user_prompt_template(self) -> str:
        """변수가 포함된 사용자 프롬프트 템플릿 반환."""
        return self._get_template().get("user_prompt_template", "")

    def get_improvement_prompt_template(self) -> str:
        """2단계: 개선 요청 프롬프트 템플릿 반환."""
        return self._get_template().get("improvement_prompt_template", "")

    # ===== 개선 변수 (공통 구현) =====

    def build_improvement_variables(
        self,
        context: ReviewContext,
        evaluation: EvaluationResult
    ) -> dict:
        """2단계: 평가 결과를 포함한 변수 딕셔너리 생성."""
        base_variables = self.build_prompt_variables(context)
        return {
            **base_variables,
            "evaluation_summary": evaluation.summary,
            "strengths": self._format_list(evaluation.strengths),
            "weaknesses": self._format_list(evaluation.weaknesses),
        }

    def _format_list(self, items: list[str]) -> str:
        """리스트를 bullet point로 포맷팅."""
        if not items:
            return "- 없음"
        return "\n".join(f"- {item}" for item in items)
