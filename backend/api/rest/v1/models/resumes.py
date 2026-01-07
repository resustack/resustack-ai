from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class WorkExperience:
    """경력 도메인 모델"""

    company_name: str  # 회사명
    period: str  # 재직 기간
    tech_stack: list[str]  # 관련 기술 스택
    link: str | None  # 관련 링크
    content: str  # 경력 내용


@dataclass(frozen=True)
class Project:
    """프로젝트 도메인 모델"""

    project_title: str  # 프로젝트 제목
    period: str  # 프로젝트 기간
    tech_stack: list[str]  # 기술 스택
    link: str | None  # 프로젝트 링크
    content: str  # 프로젝트 내용


@dataclass(frozen=True)
class Education:
    """교육 도메인 모델"""

    education_name: str  # 교육명/과정명
    period: str  # 교육 기간
    tech_stack: list[str]  # 학습한 기술
    link: str | None  # 수료증/링크
    position: str  # 목표 직무
    content: str  # 교육 내용


@dataclass(frozen=True)
class Introduction:
    """소개글 도메인 모델"""

    name: str  # 이름
    position: str  # 직무
    work_experiences: list[WorkExperience]  # 경력 내용들
    projects: list[Project]  # 프로젝트 내용들
    content: str  # 현재 소개글


@dataclass(frozen=True)
class TechSkill:
    """기술 스킬 도메인 모델"""

    dev_ops: list[str]  # DevOps 스킬
    language: list[str]  # 프로그래밍 언어
    framework: list[str]  # 프레임워크
    database: list[str]  # 데이터베이스
    tools: list[str]  # 도구
    library: list[str]  # 라이브러리
    testing: list[str]  # 테스팅 도구
    collaboration: list[str]  # 협업 도구

@dataclass(frozen=True)
class ImprovedBlock:
    """개선된 블록"""

    block_id: UUID  # 블록 ID
    improved_content: str  # 개선된 블록 내용


@dataclass(frozen=True)
class AIReviewResult:
    """AI 리뷰 결과 모델"""

    resume_id: UUID  # 이력서 ID
    evaluation_result: str  # 전체 평가 결과
    improvement_suggestion: str  # 전체 개선 제안
    improved_resume_blocks_content: list[ImprovedBlock] = field(default_factory=list)  # 개선된 이력서 블록 
