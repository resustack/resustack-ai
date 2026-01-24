"""도메인 모델 테스트."""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.domain.resume.enums import SectionType
from backend.domain.resume.models import Block, Profile, Resume, Section, Skills


class TestProfile:
    """Profile 모델 테스트."""

    def test_profile_creation_success(self) -> None:
        """정상적인 Profile 생성."""
        profile = Profile(
            name="홍길동",
            position="백엔드 개발자",
            introduction="FastAPI와 Python을 활용한 백엔드 개발 3년차",
            email="hong@example.com",
            phone="010-1234-5678",
            github="https://github.com/honggildong",
            blog="https://blog.example.com",
        )

        assert profile.name == "홍길동"
        assert profile.position == "백엔드 개발자"
        assert profile.email == "hong@example.com"

    def test_profile_with_camel_case_input(self) -> None:
        """camelCase 입력도 정상 처리."""
        data = {
            "name": "홍길동",
            "position": "개발자",
            "introduction": "소개",
            "email": "test@test.com",
            "phone": "010-1111-2222",
            "photoUrl": "https://example.com/photo.jpg",  # camelCase
        }
        profile = Profile(**data)

        assert str(profile.photo_url) == "https://example.com/photo.jpg"

    def test_profile_validation_error_empty_name(self) -> None:
        """이름이 빈 문자열이면 실패."""
        with pytest.raises(ValidationError) as exc_info:
            Profile(
                name="",  # 빈 문자열
                position="개발자",
                introduction="소개",
                email="test@test.com",
                phone="010-1111-2222",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_profile_validation_error_too_long_name(self) -> None:
        """이름이 100자를 초과하면 실패."""
        with pytest.raises(ValidationError) as exc_info:
            Profile(
                name="가" * 101,  # 101자
                position="개발자",
                introduction="소개",
                email="test@test.com",
                phone="010-1111-2222",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)


class TestBlock:
    """Block 모델 테스트."""

    def test_block_creation_success(self) -> None:
        """정상적인 Block 생성."""
        block_id = uuid4()
        block = Block(
            id=block_id,
            sub_title="AI 챗봇 서비스 개발",
            period="2023.01 - 2023.12",
            content="FastAPI 기반 챗봇 백엔드 구축",
            is_visible=True,
            tech_stack=["Python", "FastAPI", "PostgreSQL"],
            link="https://github.com/example/project",
        )

        assert block.id == block_id
        assert block.sub_title == "AI 챗봇 서비스 개발"
        assert len(block.tech_stack) == 3
        assert "FastAPI" in block.tech_stack

    def test_block_tech_stack_empty_list(self) -> None:
        """tech_stack이 빈 리스트면 정상 처리."""
        block = Block(
            id=uuid4(),
            sub_title="프로젝트",
            period="2023.01 - 2023.12",
            content="내용",
            is_visible=True,
            tech_stack=[],  # 빈 리스트
        )

        assert block.tech_stack == []

    def test_block_tech_stack_validation_error_too_long_item(self) -> None:
        """tech_stack 항목이 100자 초과 시 실패."""
        with pytest.raises(ValueError, match="100자를 초과할 수 없습니다"):
            Block(
                id=uuid4(),
                sub_title="프로젝트",
                period="2023.01 - 2023.12",
                content="내용",
                is_visible=True,
                tech_stack=["A" * 101],  # 101자 항목
            )

    def test_block_tech_stack_validation_error_empty_string(self) -> None:
        """tech_stack에 빈 문자열이 있으면 실패."""
        with pytest.raises(ValueError, match="빈 문자열일 수 없습니다"):
            Block(
                id=uuid4(),
                sub_title="프로젝트",
                period="2023.01 - 2023.12",
                content="내용",
                is_visible=True,
                tech_stack=["Python", "   ", "FastAPI"],  # 공백만 있는 문자열
            )

    def test_block_content_max_length(self) -> None:
        """content가 5000자까지 허용."""
        block = Block(
            id=uuid4(),
            sub_title="프로젝트",
            period="2023.01 - 2023.12",
            content="가" * 5000,  # 5000자
            is_visible=True,
        )

        assert len(block.content) == 5000


class TestSection:
    """Section 모델 테스트."""

    def test_section_creation_with_blocks(self) -> None:
        """블록을 포함한 Section 생성."""
        section_id = uuid4()
        block1 = Block(
            id=uuid4(),
            sub_title="프로젝트 1",
            period="2023.01 - 2023.06",
            content="내용 1",
            is_visible=True,
        )
        block2 = Block(
            id=uuid4(),
            sub_title="프로젝트 2",
            period="2023.07 - 2023.12",
            content="내용 2",
            is_visible=True,
        )

        section = Section(
            id=section_id,
            type=SectionType.PROJECT,
            title="프로젝트",
            order_index=1,
            blocks=[block1, block2],
        )

        assert section.type == SectionType.PROJECT
        assert len(section.blocks) == 2
        assert section.blocks[0].sub_title == "프로젝트 1"

    def test_section_order_index_validation(self) -> None:
        """order_index는 0-100 범위."""
        with pytest.raises(ValidationError):
            Section(
                id=uuid4(),
                type=SectionType.WORK_EXPERIENCE,
                title="경력",
                order_index=101,  # 100 초과
                blocks=[],
            )

    def test_section_blocks_max_count(self) -> None:
        """최대 20개의 블록 허용."""
        blocks = [
            Block(
                id=uuid4(),
                sub_title=f"블록 {i}",
                period="2023.01 - 2023.12",
                content=f"내용 {i}",
                is_visible=True,
            )
            for i in range(20)
        ]

        section = Section(
            id=uuid4(),
            type=SectionType.PROJECT,
            title="프로젝트",
            order_index=1,
            blocks=blocks,
        )

        assert len(section.blocks) == 20


class TestSkills:
    """Skills 모델 테스트."""

    def test_skills_creation(self) -> None:
        """Skills 모델 생성."""
        skills = Skills(
            language=["Python", "TypeScript", "Go"],
            framework=["FastAPI", "React", "Next.js"],
            database=["PostgreSQL", "Redis"],
            dev_ops=["Docker", "Kubernetes"],
            tools=["Git", "GitHub Actions"],
            library=["Pydantic", "SQLAlchemy"],
            testing=["pytest", "Jest"],
            collaboration=["Slack", "Notion"],
        )

        assert len(skills.language) == 3
        assert "Python" in skills.language
        assert len(skills.framework) == 3

    def test_skills_empty_fields(self) -> None:
        """빈 필드도 정상 처리."""
        skills = Skills()

        assert skills.language == []
        assert skills.framework == []
        assert skills.database == []

    def test_skills_validation_error_too_long_item(self) -> None:
        """스킬 항목이 100자 초과 시 실패."""
        with pytest.raises(ValueError, match="100자를 초과할 수 없습니다"):
            Skills(language=["A" * 101])

    def test_skills_validation_error_empty_string(self) -> None:
        """빈 문자열 스킬 항목 실패."""
        with pytest.raises(ValueError, match="빈 문자열일 수 없습니다"):
            Skills(language=["Python", "  "])


class TestResume:
    """Resume 모델 테스트."""

    def test_resume_creation_full(self) -> None:
        """전체 Resume 생성."""
        resume_id = "507f1f77bcf86cd799439011"
        now = datetime.now()

        profile = Profile(
            name="홍길동",
            position="백엔드 개발자",
            introduction="소개글",
            email="test@test.com",
            phone="010-1111-2222",
        )

        section = Section(
            id=uuid4(),
            type=SectionType.WORK_EXPERIENCE,
            title="경력",
            order_index=0,
            blocks=[],
        )

        skills = Skills(language=["Python", "Go"])

        resume = Resume(
            id=resume_id,
            user_id=123,
            title="홍길동 이력서",
            template_id=1,
            status="draft",
            is_public=False,
            profile=profile,
            sections=[section],
            skills=skills,
            created_at=now,
            updated_at=now,
        )

        assert resume.id == resume_id
        assert resume.user_id == 123
        assert resume.title == "홍길동 이력서"
        assert resume.profile.name == "홍길동"
        assert len(resume.sections) == 1

    def test_resume_with_alias_id(self) -> None:
        """_id alias로 id 필드 입력 가능."""
        data = {
            "_id": "507f1f77bcf86cd799439011",
            "userId": 1,
            "title": "이력서",
            "templateId": 1,
            "status": "draft",
            "isPublic": False,
            "profile": {
                "name": "홍길동",
                "position": "개발자",
                "introduction": "소개",
                "email": "test@test.com",
                "phone": "010-1111-2222",
            },
            "skills": {},
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        }

        resume = Resume(**data)
        assert resume.id == "507f1f77bcf86cd799439011"

    def test_resume_sections_max_count(self) -> None:
        """최대 10개 섹션 허용."""
        profile = Profile(
            name="홍길동",
            position="개발자",
            introduction="소개",
            email="test@test.com",
            phone="010-1111-2222",
        )

        sections = [
            Section(
                id=uuid4(),
                type=SectionType.PROJECT,
                title=f"섹션 {i}",
                order_index=i,
                blocks=[],
            )
            for i in range(10)
        ]

        resume = Resume(
            id="507f1f77bcf86cd799439011",
            user_id=1,
            title="이력서",
            template_id=1,
            status="draft",
            is_public=False,
            profile=profile,
            sections=sections,
            skills=Skills(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert len(resume.sections) == 10
