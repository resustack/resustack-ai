from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic.alias_generators import to_camel
from pydantic_core import Url

from backend.domain.resume.enums import SectionType

# 도메인 모델용 ConfigDict (camelCase 입력 허용)
DOMAIN_CONFIG = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
)


class Profile(BaseModel):
    """프로필 모델"""

    model_config = DOMAIN_CONFIG

    name: str = Field(..., min_length=1, max_length=100, description="이름")
    position: str = Field(..., min_length=1, max_length=100, description="직무")
    introduction: str = Field(..., min_length=1, max_length=2000, description="소개글")
    email: EmailStr = Field(..., min_length=1, max_length=255, description="이메일")
    phone: str = Field(..., min_length=1, max_length=50, description="전화번호")
    github: Url | None = Field(None, description="깃허브")
    blog: Url | None = Field(None, description="블로그")
    photo_url: Url | None = Field(None, description="프로필 사진")


class Block(BaseModel):
    """Section 영역에서 차지하는 모델"""

    model_config = DOMAIN_CONFIG

    id: UUID = Field(..., description="블록 ID")
    sub_title: str = Field(..., min_length=1, max_length=200, description="블록 부제목")
    period: str = Field(..., min_length=1, max_length=100, description="기간")
    content: str = Field(..., min_length=1, max_length=5000, description="블록 주요 내용")
    is_visible: bool = Field(..., description="블록 표시 여부")
    tech_stack: list[str] = Field(default_factory=list, max_length=50, description="관련 기술 스택")
    link: Url | None = Field(None, description="관련 링크")

    @field_validator("tech_stack")
    @classmethod
    def validate_tech_stack_items(cls, v: list[str]) -> list[str]:
        """각 기술 스택 항목의 길이 검증."""
        for item in v:
            if len(item) > 100:
                raise ValueError("각 기술 스택 항목은 100자를 초과할 수 없습니다")
            if len(item.strip()) == 0:
                raise ValueError("기술 스택 항목은 빈 문자열일 수 없습니다")
        return v


class Section(BaseModel):
    """이력서에서 차지하는 논리적인 단위 모델"""

    model_config = DOMAIN_CONFIG

    id: UUID = Field(..., description="섹션 ID")
    type: SectionType = Field(..., description="섹션 타입")
    title: str = Field(..., min_length=1, max_length=100, description="섹션 제목")
    order_index: int = Field(..., ge=0, le=100, description="섹션 순서")
    blocks: list[Block] = Field(default_factory=list, max_length=20, description="섹션 블록")


class Skills(BaseModel):
    """스킬 모델"""

    model_config = DOMAIN_CONFIG

    dev_ops: list[str] = Field(default_factory=list, max_length=30, description="DevOps 스킬")
    language: list[str] = Field(default_factory=list, max_length=30, description="프로그래밍 언어")
    framework: list[str] = Field(default_factory=list, max_length=30, description="프레임워크")
    database: list[str] = Field(default_factory=list, max_length=30, description="데이터베이스")
    tools: list[str] = Field(default_factory=list, max_length=30, description="도구")
    library: list[str] = Field(default_factory=list, max_length=30, description="라이브러리")
    testing: list[str] = Field(default_factory=list, max_length=30, description="테스팅 도구")
    collaboration: list[str] = Field(default_factory=list, max_length=30, description="협업 도구")

    @field_validator(
        "dev_ops", "language", "framework", "database",
        "tools", "library", "testing", "collaboration"
    )
    @classmethod
    def validate_skill_items(cls, v: list[str]) -> list[str]:
        """각 스킬 항목의 길이 검증."""
        for item in v:
            if len(item) > 100:
                raise ValueError("각 스킬 항목은 100자를 초과할 수 없습니다")
            if len(item.strip()) == 0:
                raise ValueError("스킬 항목은 빈 문자열일 수 없습니다")
        return v


class Resume(BaseModel):
    """이력서 모델"""

    model_config = DOMAIN_CONFIG

    id: str = Field(..., alias="_id", description="이력서 ID")
    user_id: int = Field(..., ge=1, description="사용자 ID")
    title: str = Field(..., min_length=1, max_length=200, description="이력서 제목")
    template_id: int = Field(..., ge=1, description="템플릿 ID")
    status: str = Field(..., min_length=1, max_length=50, description="이력서 상태")
    is_public: bool = Field(..., description="공개 여부")
    profile: Profile = Field(..., description="프로필 정보")
    sections: list[Section] = Field(default_factory=list, max_length=10, description="섹션 목록")
    skills: Skills = Field(..., description="스킬")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")
