"""Pytest configuration and fixtures."""

from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.api.rest.main import app
from backend.domain.resume.enums import SectionType
from backend.domain.resume.models import Block, Profile, Resume, Section, Skills


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_profile() -> Profile:
    """샘플 Profile 데이터."""
    return Profile(
        name="홍길동",
        position="백엔드 개발자",
        introduction="FastAPI와 Python을 활용한 백엔드 개발 3년차입니다.",
        email="hong@example.com",
        phone="010-1234-5678",
        github="https://github.com/honggildong",
        blog="https://blog.example.com",
    )


@pytest.fixture
def sample_skills() -> Skills:
    """샘플 Skills 데이터."""
    return Skills(
        language=["Python", "TypeScript", "Go"],
        framework=["FastAPI", "React", "Next.js"],
        database=["PostgreSQL", "Redis", "MongoDB"],
        dev_ops=["Docker", "Kubernetes", "GitHub Actions"],
        tools=["Git", "VS Code"],
        library=["Pydantic", "SQLAlchemy"],
        testing=["pytest", "Jest"],
        collaboration=["Slack", "Notion"],
    )


@pytest.fixture
def sample_block() -> Block:
    """샘플 Block 데이터."""
    return Block(
        id=uuid4(),
        sub_title="AI 챗봇 서비스 개발",
        period="2023.01 - 2023.12",
        content="FastAPI 기반 챗봇 백엔드 시스템 설계 및 구현. REST API 20개 개발, 응답 속도 50% 개선.",
        is_visible=True,
        tech_stack=["Python", "FastAPI", "PostgreSQL", "Redis"],
        link="https://github.com/example/chatbot",
    )


@pytest.fixture
def sample_section(sample_block: Block) -> Section:
    """샘플 Section 데이터."""
    return Section(
        id=uuid4(),
        type=SectionType.PROJECT,
        title="프로젝트",
        order_index=0,
        blocks=[sample_block],
    )


@pytest.fixture
def sample_resume(sample_profile: Profile, sample_section: Section, sample_skills: Skills) -> Resume:
    """샘플 Resume 데이터."""
    return Resume(
        id="507f1f77bcf86cd799439011",
        user_id=123,
        title="홍길동 백엔드 개발자 이력서",
        template_id=1,
        status="draft",
        is_public=False,
        profile=sample_profile,
        sections=[sample_section],
        skills=sample_skills,
        created_at=datetime(2024, 1, 1, 0, 0, 0),
        updated_at=datetime(2024, 1, 1, 0, 0, 0),
    )
