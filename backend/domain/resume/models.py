from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic_core import Url

from backend.domain.resume.enums import SectionType


class Profile(BaseModel):
    """프로필 모델"""

    name: str = Field(..., description="이름")
    position: str = Field(..., description="직무")
    introduction: str = Field(..., description="소개글")
    email: str = Field(..., description="이메일")
    phone: str = Field(..., description="전화번호")
    github: Url | None = Field(None, description="깃허브")
    blog: Url | None = Field(None, description="블로그")
    photo_url: Url | None = Field(None, description="프로필 사진")


class Block(BaseModel):
    """Section 영역에서 차지하는 모델"""

    id: UUID = Field(..., description="블록 ID")
    sub_title: str = Field(..., description="블록 부제목")
    period: str = Field(..., description="기간")
    content: str = Field(..., description="블록 주요 내용")
    is_visible: bool = Field(..., description="블록 표시 여부")
    tech_stack: list[str] = Field(..., description="관련 기술 스택")
    link: Url | None = Field(None, description="관련 링크")


class Section(BaseModel):
    """이력서에서 차지하는 논리적인 단위 모델"""

    id: UUID = Field(..., description="섹션 ID")
    type: SectionType = Field(..., description="섹션 타입")
    title: str = Field(..., description="섹션 제목")
    order_index: int = Field(..., description="섹션 순서")
    blocks: list[Block] = Field(..., description="섹션 블록")


class Skills(BaseModel):
    """스킬 모델"""

    dev_ops: list[str] = Field(..., description="DevOps 스킬")
    language: list[str] = Field(..., description="프로그래밍 언어")
    framework: list[str] = Field(..., description="프레임워크")
    database: list[str] = Field(..., description="데이터베이스")
    tools: list[str] = Field(..., description="도구")
    library: list[str] = Field(..., description="라이브러리")
    testing: list[str] = Field(..., description="테스팅 도구")
    collaboration: list[str] = Field(..., description="협업 도구")


class Resume(BaseModel):
    """이력서 모델"""

    id: str = Field(..., alias="_id", description="이력서 ID")
    user_id: int = Field(..., description="사용자 ID")
    title: str = Field(..., description="이력서 제목")
    template_id: int = Field(..., description="템플릿 ID")
    status: str = Field(..., description="이력서 상태")
    is_public: bool = Field(..., description="공개 여부")
    profile: Profile = Field(..., description="프로필 정보")
    sections: list[Section] = Field(..., description="섹션 목록")
    skills: Skills = Field(..., description="스킬")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")
