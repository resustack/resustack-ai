"""ReviewContextAssembler 테스트."""

from datetime import datetime
from uuid import uuid4

import pytest
from backend.api.rest.v1.schemas.resumes import (
    ResumeBlockReviewRequest,
    ResumeReviewRequest,
    ResumeSectionReviewRequest,
    ResumeSkillReviewRequest,
)
from backend.domain.resume.enums import SectionType
from backend.domain.resume.models import Block, Profile, Section, Skills
from backend.services.review.assembler import (
    ReviewContextAssembler,
    get_review_context_assembler,
)
from backend.services.review.enums import ReviewTargetType


@pytest.fixture
def assembler() -> ReviewContextAssembler:
    """ReviewContextAssembler 인스턴스."""
    return ReviewContextAssembler()


@pytest.fixture
def sample_profile() -> Profile:
    """샘플 Profile."""
    return Profile(
        name="홍길동",
        position="백엔드 개발자",
        introduction="FastAPI와 Python을 활용한 백엔드 개발 3년차입니다.",
        email="hong@example.com",
        phone="010-1234-5678",
    )


@pytest.fixture
def sample_skills() -> Skills:
    """샘플 Skills."""
    return Skills(
        language=["Python", "TypeScript"],
        framework=["FastAPI", "React"],
        database=["PostgreSQL", "Redis"],
        dev_ops=["Docker", "Kubernetes"],
        tools=["Git", "VS Code"],
        library=["Pydantic", "SQLAlchemy"],
        testing=["pytest"],
        collaboration=["Slack"],
    )


@pytest.fixture
def sample_block() -> Block:
    """샘플 Block."""
    return Block(
        id=uuid4(),
        sub_title="AI 챗봇 서비스 개발",
        period="2023.01 - 2023.12",
        content="FastAPI 기반 챗봇 백엔드 구축",
        is_visible=True,
        tech_stack=["Python", "FastAPI", "PostgreSQL"],
        link="https://github.com/example/project",
    )


@pytest.fixture
def sample_section(sample_block: Block) -> Section:
    """샘플 Section."""
    return Section(
        id=uuid4(),
        type=SectionType.PROJECT,
        title="프로젝트",
        order_index=0,
        blocks=[sample_block],
    )


def create_resume_review_request(
    profile: Profile,
    sections: list[Section] | None = None,
    skills: Skills | None = None,
) -> ResumeReviewRequest:
    """ResumeReviewRequest 헬퍼 함수."""
    now = datetime.now()
    return ResumeReviewRequest(
        _id="507f1f77bcf86cd799439011",
        user_id=1,
        title="테스트 이력서",
        template_id=1,
        status="draft",
        is_public=False,
        profile=profile,
        sections=sections or [],
        skills=skills or Skills(),
        created_at=now,
        updated_at=now,
    )


class TestAssembleFull:
    """전체 이력서 컨텍스트 조립 테스트."""

    def test_assemble_full_basic(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """기본적인 전체 이력서 컨텍스트 조립."""
        resume_id = uuid4()
        request = create_resume_review_request(profile=sample_profile)

        context = assembler.assemble_full(resume_id, request)

        assert context.resume_id == resume_id
        assert context.target_type == ReviewTargetType.RESUME_FULL
        assert context.full_resume_text is not None
        assert "홍길동" in context.full_resume_text
        assert "백엔드 개발자" in context.full_resume_text

    def test_assemble_full_with_skills(
        self,
        assembler: ReviewContextAssembler,
        sample_profile: Profile,
        sample_skills: Skills,
    ) -> None:
        """스킬이 포함된 전체 이력서 컨텍스트 조립."""
        resume_id = uuid4()
        request = create_resume_review_request(
            profile=sample_profile,
            skills=sample_skills,
        )

        context = assembler.assemble_full(resume_id, request)

        assert "Python" in context.full_resume_text
        assert "FastAPI" in context.full_resume_text
        assert "PostgreSQL" in context.full_resume_text

    def test_assemble_full_with_sections(
        self,
        assembler: ReviewContextAssembler,
        sample_profile: Profile,
        sample_section: Section,
    ) -> None:
        """섹션이 포함된 전체 이력서 컨텍스트 조립."""
        resume_id = uuid4()
        request = create_resume_review_request(
            profile=sample_profile,
            sections=[sample_section],
        )

        context = assembler.assemble_full(resume_id, request)

        assert "프로젝트" in context.full_resume_text
        assert "AI 챗봇 서비스 개발" in context.full_resume_text


class TestAssembleIntroduction:
    """소개글 컨텍스트 조립 테스트."""

    def test_assemble_introduction_basic(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """기본적인 소개글 컨텍스트 조립."""
        resume_id = uuid4()
        request = create_resume_review_request(profile=sample_profile)

        context = assembler.assemble_introduction(resume_id, request)

        assert context.resume_id == resume_id
        assert context.target_type == ReviewTargetType.INTRODUCTION
        assert context.introduction is not None
        assert context.introduction.name == "홍길동"
        assert context.introduction.position == "백엔드 개발자"
        assert context.introduction.content == sample_profile.introduction

    def test_assemble_introduction_with_work_experience(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """경력 정보가 포함된 소개글 컨텍스트 조립."""
        resume_id = uuid4()
        work_block = Block(
            id=uuid4(),
            sub_title="ABC 회사",
            period="2021.01 - 2023.12",
            content="백엔드 시스템 개발 담당",
            is_visible=True,
        )
        work_section = Section(
            id=uuid4(),
            type=SectionType.WORK_EXPERIENCE,
            title="경력",
            order_index=0,
            blocks=[work_block],
        )

        request = create_resume_review_request(
            profile=sample_profile,
            sections=[work_section],
        )

        context = assembler.assemble_introduction(resume_id, request)

        assert "ABC 회사" in context.introduction.work_experience_summary
        assert "2021.01 - 2023.12" in context.introduction.work_experience_summary

    def test_assemble_introduction_with_project(
        self,
        assembler: ReviewContextAssembler,
        sample_profile: Profile,
        sample_section: Section,
    ) -> None:
        """프로젝트 정보가 포함된 소개글 컨텍스트 조립."""
        resume_id = uuid4()
        request = create_resume_review_request(
            profile=sample_profile,
            sections=[sample_section],
        )

        context = assembler.assemble_introduction(resume_id, request)

        assert "AI 챗봇 서비스 개발" in context.introduction.project_summary

    def test_assemble_introduction_no_sections(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """섹션이 없을 때 기본값 확인."""
        resume_id = uuid4()
        request = create_resume_review_request(profile=sample_profile)

        context = assembler.assemble_introduction(resume_id, request)

        assert context.introduction.work_experience_summary == "없음"
        assert context.introduction.project_summary == "없음"


class TestAssembleSkill:
    """스킬 컨텍스트 조립 테스트."""

    def test_assemble_skill_full(
        self,
        assembler: ReviewContextAssembler,
        sample_profile: Profile,
        sample_skills: Skills,
    ) -> None:
        """전체 스킬 컨텍스트 조립."""
        resume_id = uuid4()
        request = ResumeSkillReviewRequest(
            profile=sample_profile,
            skills=sample_skills,
        )

        context = assembler.assemble_skill(resume_id, request)

        assert context.resume_id == resume_id
        assert context.target_type == ReviewTargetType.SKILL
        assert context.skill is not None
        assert context.skill.language == ["Python", "TypeScript"]
        assert context.skill.framework == ["FastAPI", "React"]
        assert context.skill.database == ["PostgreSQL", "Redis"]
        assert context.skill.dev_ops == ["Docker", "Kubernetes"]

    def test_assemble_skill_empty(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """빈 스킬 컨텍스트 조립."""
        resume_id = uuid4()
        request = ResumeSkillReviewRequest(
            profile=sample_profile,
            skills=Skills(),
        )

        context = assembler.assemble_skill(resume_id, request)

        assert context.skill.language == []
        assert context.skill.framework == []


class TestAssembleSection:
    """섹션 컨텍스트 조립 테스트."""

    def test_assemble_section_project(
        self,
        assembler: ReviewContextAssembler,
        sample_profile: Profile,
        sample_block: Block,
    ) -> None:
        """프로젝트 섹션 컨텍스트 조립."""
        resume_id = uuid4()
        section_id = uuid4()

        request = ResumeSectionReviewRequest(
            id=section_id,
            type=SectionType.PROJECT,
            title="프로젝트",
            order_index=0,
            blocks=[sample_block],
            profile=sample_profile,
        )

        context = assembler.assemble_section(resume_id, SectionType.PROJECT, request)

        assert context.resume_id == resume_id
        assert context.target_type == ReviewTargetType.PROJECT
        assert context.section is not None
        assert context.section.section_id == section_id
        assert context.section.section_type == SectionType.PROJECT
        assert len(context.section.blocks) == 1
        assert context.section.blocks[0].sub_title == "AI 챗봇 서비스 개발"

    def test_assemble_section_work_experience(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """경력 섹션 컨텍스트 조립."""
        resume_id = uuid4()
        section_id = uuid4()
        block = Block(
            id=uuid4(),
            sub_title="ABC 회사",
            period="2021.01 - 2023.12",
            content="백엔드 시스템 개발",
            is_visible=True,
        )

        request = ResumeSectionReviewRequest(
            id=section_id,
            type=SectionType.WORK_EXPERIENCE,
            title="경력",
            order_index=0,
            blocks=[block],
            profile=sample_profile,
        )

        context = assembler.assemble_section(
            resume_id, SectionType.WORK_EXPERIENCE, request
        )

        assert context.target_type == ReviewTargetType.WORK_EXPERIENCE

    def test_assemble_section_multiple_blocks(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """여러 블록이 있는 섹션 컨텍스트 조립."""
        resume_id = uuid4()
        section_id = uuid4()
        blocks = [
            Block(
                id=uuid4(),
                sub_title=f"프로젝트 {i}",
                period=f"2023.0{i} - 2023.0{i+1}",
                content=f"프로젝트 {i} 내용",
                is_visible=True,
                tech_stack=["Python"],
            )
            for i in range(1, 4)
        ]

        request = ResumeSectionReviewRequest(
            id=section_id,
            type=SectionType.PROJECT,
            title="프로젝트",
            order_index=0,
            blocks=blocks,
            profile=sample_profile,
        )

        context = assembler.assemble_section(resume_id, SectionType.PROJECT, request)

        assert len(context.section.blocks) == 3
        assert context.section.blocks[0].sub_title == "프로젝트 1"
        assert context.section.blocks[2].sub_title == "프로젝트 3"


class TestAssembleBlock:
    """블록 컨텍스트 조립 테스트."""

    def test_assemble_block_project(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """프로젝트 블록 컨텍스트 조립."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id = uuid4()

        request = ResumeBlockReviewRequest(
            id=block_id,
            sub_title="AI 챗봇 서비스",
            period="2023.01 - 2023.12",
            content="FastAPI 기반 챗봇 백엔드 구축",
            is_visible=True,
            tech_stack=["Python", "FastAPI"],
            profile=sample_profile,
        )

        context = assembler.assemble_block(
            resume_id, SectionType.PROJECT, section_id, block_id, request
        )

        assert context.resume_id == resume_id
        assert context.target_type == ReviewTargetType.PROJECT_BLOCK
        assert context.block is not None
        assert context.block.block_id == block_id
        assert context.block.sub_title == "AI 챗봇 서비스"
        assert context.block.tech_stack == ["Python", "FastAPI"]

    def test_assemble_block_work_experience(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """경력 블록 컨텍스트 조립."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id = uuid4()

        request = ResumeBlockReviewRequest(
            id=block_id,
            sub_title="ABC 회사",
            period="2021.01 - 2023.12",
            content="백엔드 시스템 개발",
            is_visible=True,
            profile=sample_profile,
        )

        context = assembler.assemble_block(
            resume_id, SectionType.WORK_EXPERIENCE, section_id, block_id, request
        )

        assert context.target_type == ReviewTargetType.WORK_EXPERIENCE_BLOCK

    def test_assemble_block_with_link(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """링크가 포함된 블록 컨텍스트 조립."""
        resume_id = uuid4()
        section_id = uuid4()
        block_id = uuid4()

        request = ResumeBlockReviewRequest(
            id=block_id,
            sub_title="오픈소스 프로젝트",
            period="2023.01 - 2023.06",
            content="오픈소스 기여",
            is_visible=True,
            link="https://github.com/example/project",
            profile=sample_profile,
        )

        context = assembler.assemble_block(
            resume_id, SectionType.PROJECT, section_id, block_id, request
        )

        assert context.block.link == "https://github.com/example/project"


class TestPreprocessSection:
    """섹션 전처리 테스트."""

    def test_preprocess_section_found(
        self,
        assembler: ReviewContextAssembler,
        sample_profile: Profile,
        sample_section: Section,
    ) -> None:
        """섹션이 존재할 때 요약 생성."""
        request = create_resume_review_request(
            profile=sample_profile,
            sections=[sample_section],
        )

        result = assembler._preprocess_section(request, SectionType.PROJECT)

        assert "AI 챗봇 서비스 개발" in result
        assert "2023.01 - 2023.12" in result

    def test_preprocess_section_not_found(
        self, assembler: ReviewContextAssembler, sample_profile: Profile
    ) -> None:
        """섹션이 없을 때 '없음' 반환."""
        request = create_resume_review_request(profile=sample_profile)

        result = assembler._preprocess_section(request, SectionType.WORK_EXPERIENCE)

        assert result == "없음"


class TestGetReviewContextAssembler:
    """싱글톤 인스턴스 테스트."""

    def test_singleton_instance(self) -> None:
        """같은 인스턴스가 반환되는지 확인."""
        instance1 = get_review_context_assembler()
        instance2 = get_review_context_assembler()

        assert instance1 is instance2
        assert isinstance(instance1, ReviewContextAssembler)
