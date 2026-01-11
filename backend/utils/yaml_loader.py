"""YAML 파일 로더 유틸리티."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


def _get_prompts_dir() -> Path:
    """프롬프트 템플릿 디렉토리 경로 반환."""
    return Path(__file__).parent.parent / "ai" / "prompts" / "templates"


@lru_cache(maxsize=32)
def load_prompt_template(template_name: str) -> dict[str, Any]:
    """YAML 프롬프트 템플릿 로드 (캐싱 적용).

    Args:
        template_name: 템플릿 파일 이름 (확장자 제외)

    Returns:
        dict: 프롬프트 템플릿 데이터

    Raises:
        FileNotFoundError: 템플릿 파일이 없는 경우
    """
    template_path = _get_prompts_dir() / f"{template_name}.yaml"

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_prompt(template_name: str, key: str) -> str:
    """특정 프롬프트 템플릿에서 키에 해당하는 프롬프트 반환.

    Args:
        template_name: 템플릿 파일 이름 (확장자 제외)
        key: 프롬프트 키 (예: 'specific_instructions', 'evaluation_instructions')

    Returns:
        str: 프롬프트 문자열

    Raises:
        KeyError: 키가 없는 경우
    """
    template = load_prompt_template(template_name)
    if key not in template:
        raise KeyError(f"Key '{key}' not found in template '{template_name}'")
    return template[key]


def clear_prompt_cache() -> None:
    """프롬프트 템플릿 캐시 초기화 (테스트용)."""
    load_prompt_template.cache_clear()
