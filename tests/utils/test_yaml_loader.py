"""YAML 로더 유틸리티 테스트."""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from backend.utils.yaml_loader import (
    _get_prompts_dir,
    clear_prompt_cache,
    get_prompt,
    load_prompt_template,
)


class TestGetPromptsDir:
    """프롬프트 디렉토리 경로 테스트."""

    def test_get_prompts_dir_returns_correct_path(self) -> None:
        """프롬프트 디렉토리 경로 반환."""
        prompts_dir = _get_prompts_dir()

        assert isinstance(prompts_dir, Path)
        assert prompts_dir.name == "templates"
        assert "prompts" in str(prompts_dir)
        assert "ai" in str(prompts_dir)


class TestLoadPromptTemplate:
    """프롬프트 템플릿 로드 테스트."""

    def setup_method(self) -> None:
        """각 테스트 전 캐시 초기화."""
        clear_prompt_cache()

    def test_load_prompt_template_success(self) -> None:
        """정상적인 템플릿 로드."""
        # 실제 파일이 있는 경우 테스트
        # 실제 프로젝트에 있는 템플릿 파일을 사용
        template_name = "introduction"  # 실제 존재하는 템플릿명으로 변경

        # 템플릿 파일이 실제로 존재하는 경우만 테스트
        try:
            result = load_prompt_template(template_name)
            assert isinstance(result, dict)
        except FileNotFoundError:
            pytest.skip(f"Template {template_name} not found - skip test")

    def test_load_prompt_template_file_not_found(self) -> None:
        """존재하지 않는 템플릿 파일."""
        with pytest.raises(FileNotFoundError, match="Template not found"):
            load_prompt_template("nonexistent_template")

    def test_load_prompt_template_caching(self) -> None:
        """템플릿 캐싱 확인."""
        mock_yaml_content = {"key1": "value1", "key2": "value2"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open", mock_open(read_data="key1: value1\nkey2: value2")
            ):
                with patch("yaml.safe_load", return_value=mock_yaml_content) as mock_yaml:
                    # 첫 번째 호출
                    result1 = load_prompt_template("test_template")
                    # 두 번째 호출 (캐시에서 가져옴)
                    result2 = load_prompt_template("test_template")

                    # yaml.safe_load는 한 번만 호출되어야 함 (캐싱)
                    assert mock_yaml.call_count == 1
                    assert result1 == result2
                    assert result1 == mock_yaml_content

    def test_load_prompt_template_different_files(self) -> None:
        """다른 템플릿 파일은 각각 로드."""
        mock_yaml1 = {"intro": "소개글"}
        mock_yaml2 = {"skill": "스킬"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load") as mock_yaml:
                    # 첫 번째 템플릿
                    mock_yaml.return_value = mock_yaml1
                    result1 = load_prompt_template("template1")

                    # 두 번째 템플릿
                    mock_yaml.return_value = mock_yaml2
                    result2 = load_prompt_template("template2")

                    assert result1 != result2
                    assert mock_yaml.call_count == 2


class TestGetPrompt:
    """특정 프롬프트 가져오기 테스트."""

    def setup_method(self) -> None:
        """각 테스트 전 캐시 초기화."""
        clear_prompt_cache()

    def test_get_prompt_success(self) -> None:
        """정상적인 프롬프트 가져오기."""
        mock_template = {
            "specific_instructions": "구체적인 지시사항입니다",
            "evaluation_instructions": "평가 지시사항입니다",
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value=mock_template):
                    result = get_prompt("test_template", "specific_instructions")

                    assert result == "구체적인 지시사항입니다"

    def test_get_prompt_key_not_found(self) -> None:
        """존재하지 않는 키."""
        mock_template = {"existing_key": "value"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value=mock_template):
                    with pytest.raises(KeyError, match="Key 'nonexistent_key' not found"):
                        get_prompt("test_template", "nonexistent_key")

    def test_get_prompt_multiple_keys(self) -> None:
        """여러 키 가져오기."""
        mock_template = {
            "key1": "값1",
            "key2": "값2",
            "key3": "값3",
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value=mock_template):
                    assert get_prompt("test", "key1") == "값1"
                    assert get_prompt("test", "key2") == "값2"
                    assert get_prompt("test", "key3") == "값3"


class TestClearPromptCache:
    """캐시 초기화 테스트."""

    def test_clear_prompt_cache(self) -> None:
        """캐시 초기화 동작 확인."""
        mock_template = {"key": "value"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value=mock_template) as mock_yaml:
                    # 첫 번째 로드
                    load_prompt_template("base")
                    assert mock_yaml.call_count == 1

                    # 캐시에서 가져옴
                    load_prompt_template("base")
                    assert mock_yaml.call_count == 1

                    # 캐시 초기화
                    clear_prompt_cache()

                    # 다시 로드 (캐시가 초기화되어 새로 읽음)
                    load_prompt_template("base")
                    assert mock_yaml.call_count == 2

    def test_cache_info(self) -> None:
        """캐시 정보 확인."""
        clear_prompt_cache()

        # 캐시 정보 확인
        cache_info = load_prompt_template.cache_info()
        assert cache_info.hits == 0
        assert cache_info.misses == 0
        assert cache_info.currsize == 0

        mock_template = {"key": "value"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value=mock_template):
                    # 첫 로드 (miss)
                    load_prompt_template("test1")
                    cache_info = load_prompt_template.cache_info()
                    assert cache_info.misses == 1
                    assert cache_info.hits == 0

                    # 같은 템플릿 재로드 (hit)
                    load_prompt_template("test1")
                    cache_info = load_prompt_template.cache_info()
                    assert cache_info.hits == 1
                    assert cache_info.misses == 1


class TestYamlLoaderEdgeCases:
    """엣지 케이스 테스트."""

    def setup_method(self) -> None:
        """각 테스트 전 캐시 초기화."""
        clear_prompt_cache()

    def test_empty_yaml_file(self) -> None:
        """빈 YAML 파일."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value=None):
                    # None이 반환되는 경우
                    result = load_prompt_template("empty")
                    assert result is None

    def test_yaml_with_korean_content(self) -> None:
        """한글 내용이 포함된 YAML."""
        mock_template = {
            "system_message": "당신은 이력서 리뷰 전문가입니다.",
            "user_message": "다음 이력서를 검토해주세요.",
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value=mock_template):
                    result = get_prompt("korean", "system_message")
                    assert result == "당신은 이력서 리뷰 전문가입니다."
                    assert "전문가" in result

    def test_nested_yaml_structure(self) -> None:
        """중첩된 YAML 구조."""
        mock_template = {
            "prompts": {
                "introduction": "소개글 프롬프트",
                "skill": "스킬 프롬프트",
            },
            "metadata": {"version": "1.0"},
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value=mock_template):
                    result = load_prompt_template("nested")
                    assert result["prompts"]["introduction"] == "소개글 프롬프트"
                    assert result["metadata"]["version"] == "1.0"
