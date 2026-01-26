"""개선된 도메인 모델 테스트 - Factory Pattern 활용."""

from uuid import uuid4

import pytest
from backend.domain.resume.models import Block, Profile, Skills
from pydantic import ValidationError

# ============================================================================
# Test Data Factories (재사용 가능한 정상 데이터)
# ============================================================================

@pytest.fixture
def valid_profile_data() -> dict:
    """정상적인 Profile 데이터 (딕셔너리)."""
    return {
        "name": "홍길동",
        "position": "백엔드 개발자",
        "introduction": "FastAPI와 Python을 활용한 백엔드 개발 3년차",
        "email": "hong@example.com",
        "phone": "010-1234-5678",
        "github": "https://github.com/honggildong",
        "blog": "https://blog.example.com",
    }


@pytest.fixture
def valid_block_data() -> dict:
    """정상적인 Block 데이터 (딕셔너리)."""
    return {
        "id": uuid4(),
        "sub_title": "AI 챗봇 서비스 개발",
        "period": "2023.01 - 2023.12",
        "content": "FastAPI 기반 챗봇 백엔드 시스템 설계 및 구현",
        "is_visible": True,
        "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
        "link": "https://github.com/example/chatbot",
    }


@pytest.fixture
def valid_skills_data() -> dict:
    """정상적인 Skills 데이터 (딕셔너리)."""
    return {
        "language": ["Python", "TypeScript"],
        "framework": ["FastAPI", "React"],
        "database": ["PostgreSQL", "Redis"],
        "dev_ops": ["Docker", "Kubernetes"],
    }


# ============================================================================
# Profile 테스트
# ============================================================================

class TestProfile:
    """Profile 모델 테스트 - Factory Pattern 활용."""

    def test_profile_creation_success(self, valid_profile_data: dict) -> None:
        """정상적인 Profile 생성."""
        profile = Profile(**valid_profile_data)

        assert profile.name == valid_profile_data["name"]
        assert profile.position == valid_profile_data["position"]
        assert profile.email == valid_profile_data["email"]

    def test_profile_validation_error_empty_name(self, valid_profile_data: dict) -> None:
        """이름이 빈 문자열이면 실패."""
        # 정상 데이터를 기반으로 오류 부분만 수정
        invalid_data = {**valid_profile_data, "name": ""}

        with pytest.raises(ValidationError) as exc_info:
            Profile(**invalid_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_profile_validation_error_too_long_name(self, valid_profile_data: dict) -> None:
        """이름이 100자를 초과하면 실패."""
        invalid_data = {**valid_profile_data, "name": "가" * 101}

        with pytest.raises(ValidationError) as exc_info:
            Profile(**invalid_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_profile_validation_error_invalid_email(self, valid_profile_data: dict) -> None:
        """잘못된 이메일 형식."""
        # 여러 케이스를 반복문으로 테스트
        invalid_emails = ["invalid", "@example.com", "test@", ""]

        for invalid_email in invalid_emails:
            invalid_data = {**valid_profile_data, "email": invalid_email}

            with pytest.raises(ValidationError):
                Profile(**invalid_data)

    def test_profile_optional_fields_none(self, valid_profile_data: dict) -> None:
        """선택적 필드는 None 가능."""
        # 선택적 필드 제거
        data = {**valid_profile_data}
        data.pop("github", None)
        data.pop("blog", None)

        profile = Profile(**data)

        assert profile.github is None
        assert profile.blog is None

    @pytest.mark.parametrize(
        "field_name,invalid_value,expected_error",
        [
            ("name", "", "String should have at least 1 character"),
            ("name", "가" * 101, "String should have at most 100 characters"),
            ("position", "", "String should have at least 1 character"),
            ("introduction", "", "String should have at least 1 character"),
            ("introduction", "가" * 2001, "String should have at most 2000 characters"),
        ],
    )
    def test_profile_field_validation_parametrized(
        self,
        valid_profile_data: dict,
        field_name: str,
        invalid_value: str,
        expected_error: str,
    ) -> None:
        """파라미터화된 필드 검증 테스트."""
        invalid_data = {**valid_profile_data, field_name: invalid_value}

        with pytest.raises(ValidationError) as exc_info:
            Profile(**invalid_data)

        errors = exc_info.value.errors()
        assert any(field_name in str(error["loc"]) for error in errors)


# ============================================================================
# Block 테스트
# ============================================================================

class TestBlock:
    """Block 모델 테스트 - Factory Pattern 활용."""

    def test_block_creation_success(self, valid_block_data: dict) -> None:
        """정상적인 Block 생성."""
        block = Block(**valid_block_data)

        assert block.sub_title == valid_block_data["sub_title"]
        assert len(block.tech_stack) == len(valid_block_data["tech_stack"])

    def test_block_tech_stack_validation_error_too_long_item(
        self, valid_block_data: dict
    ) -> None:
        """tech_stack 항목이 100자 초과 시 실패."""
        invalid_data = {
            **valid_block_data,
            "tech_stack": ["Python", "A" * 101],  # 101자 항목
        }

        with pytest.raises(ValueError, match="100자를 초과할 수 없습니다"):
            Block(**invalid_data)

    def test_block_tech_stack_validation_error_empty_string(
        self, valid_block_data: dict
    ) -> None:
        """tech_stack에 빈 문자열이 있으면 실패."""
        invalid_data = {
            **valid_block_data,
            "tech_stack": ["Python", "   ", "FastAPI"],
        }

        with pytest.raises(ValueError, match="빈 문자열일 수 없습니다"):
            Block(**invalid_data)

    def test_block_content_max_length(self, valid_block_data: dict) -> None:
        """content가 5000자까지 허용."""
        data = {**valid_block_data, "content": "가" * 5000}
        block = Block(**data)

        assert len(block.content) == 5000

    def test_block_content_exceeds_max_length(self, valid_block_data: dict) -> None:
        """content가 5000자 초과 시 실패."""
        invalid_data = {**valid_block_data, "content": "가" * 5001}

        with pytest.raises(ValidationError):
            Block(**invalid_data)

    @pytest.mark.parametrize(
        "tech_stack,should_pass",
        [
            ([], True),  # 빈 리스트
            (["Python"], True),  # 단일 항목
            (["Python", "FastAPI", "PostgreSQL"], True),  # 여러 항목
            (["A" * 100], True),  # 100자 정확히
            (["A" * 101], False),  # 101자 초과
            (["Python", "  "], False),  # 빈 문자열 포함
        ],
    )
    def test_block_tech_stack_various_cases(
        self, valid_block_data: dict, tech_stack: list[str], should_pass: bool
    ) -> None:
        """다양한 tech_stack 케이스 테스트."""
        data = {**valid_block_data, "tech_stack": tech_stack}

        if should_pass:
            block = Block(**data)
            assert block.tech_stack == tech_stack
        else:
            with pytest.raises(ValueError):
                Block(**data)


# ============================================================================
# Skills 테스트
# ============================================================================

class TestSkills:
    """Skills 모델 테스트 - Factory Pattern 활용."""

    def test_skills_creation(self, valid_skills_data: dict) -> None:
        """Skills 모델 생성."""
        skills = Skills(**valid_skills_data)

        assert len(skills.language) == len(valid_skills_data["language"])
        assert skills.language == valid_skills_data["language"]

    def test_skills_empty_fields(self) -> None:
        """빈 필드도 정상 처리."""
        skills = Skills()

        assert skills.language == []
        assert skills.framework == []

    def test_skills_validation_error_too_long_item(self, valid_skills_data: dict) -> None:
        """스킬 항목이 100자 초과 시 실패."""
        invalid_data = {**valid_skills_data, "language": ["Python", "A" * 101]}

        with pytest.raises(ValueError, match="100자를 초과할 수 없습니다"):
            Skills(**invalid_data)

    @pytest.mark.parametrize(
        "field_name",
        [
            "language", "framework", "database", "dev_ops", "tools",
            "library", "testing", "collaboration"
        ],
    )
    def test_skills_all_fields_accept_valid_data(
        self, valid_skills_data: dict, field_name: str
    ) -> None:
        """모든 스킬 필드가 정상 데이터를 받는지 확인."""
        data = {field_name: ["Skill1", "Skill2"]}
        skills = Skills(**data)

        assert getattr(skills, field_name) == ["Skill1", "Skill2"]

    @pytest.mark.parametrize(
        "field_name",
        ["language", "framework", "database"],
    )
    def test_skills_fields_reject_too_long_items(self, field_name: str) -> None:
        """모든 스킬 필드가 100자 초과를 거부하는지 확인."""
        data = {field_name: ["A" * 101]}

        with pytest.raises(ValueError, match="100자를 초과할 수 없습니다"):
            Skills(**data)


# ============================================================================
# Helper Functions (선택적)
# ============================================================================

def create_valid_profile(**overrides) -> Profile:
    """테스트용 Profile 생성 헬퍼 함수.

    Args:
        **overrides: 기본값을 오버라이드할 필드

    Returns:
        Profile: 생성된 Profile 인스턴스
    """
    default_data = {
        "name": "홍길동",
        "position": "백엔드 개발자",
        "introduction": "FastAPI 전문가",
        "email": "hong@example.com",
        "phone": "010-1234-5678",
    }
    return Profile(**{**default_data, **overrides})


class TestHelperFunctions:
    """헬퍼 함수를 활용한 테스트 예시."""

    def test_with_helper_function_normal(self) -> None:
        """헬퍼 함수로 정상 데이터 생성."""
        profile = create_valid_profile()
        assert profile.name == "홍길동"

    def test_with_helper_function_override(self) -> None:
        """헬퍼 함수로 특정 필드만 변경."""
        profile = create_valid_profile(name="김철수", position="프론트엔드 개발자")

        assert profile.name == "김철수"
        assert profile.position == "프론트엔드 개발자"
        assert profile.email == "hong@example.com"  # 기본값 유지

    def test_with_helper_function_invalid_data(self) -> None:
        """헬퍼 함수로 잘못된 데이터 테스트."""
        with pytest.raises(ValidationError):
            create_valid_profile(name="")
