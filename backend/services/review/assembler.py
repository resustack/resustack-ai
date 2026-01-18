from functools import lru_cache
from uuid import UUID

from backend.api.rest.v1.schemas.resumes import (
    ResumeBlockReviewRequest,
    ResumeReviewRequest,
    ResumeSectionReviewRequest,
    ResumeSkillReviewRequest,
)
from backend.domain.resume.enums import SectionType
from backend.services.review.context import (
    BlockData,
    IntroductionData,
    ReviewContext,
    SectionData,
    SkillData,
)
from backend.services.review.enums import ReviewTargetType


class ReviewContextAssembler:
    """Request를 해석하여 ReviewContext를 조립하는 클래스.

    단순 Mapper가 아니라 요청 의도를 해석하여 AI에 필요한 컨텍스트를 조립합니다.
    """

    def assemble_full(
        self,
        resume_id: UUID,
        request: ResumeReviewRequest,
    ) -> ReviewContext:
        """전체 이력서 리뷰용 컨텍스트 조립."""
        lines = []

        # 프로필 섹션
        lines.append("## 프로필")
        lines.append(f"- 이름: {request.profile.name}")
        lines.append(f"- 직무: {request.profile.position}")
        lines.append(f"- 소개글: {request.profile.introduction}")
        lines.append("")

        # 스킬 섹션
        lines.append("## 스킬")
        skill_labels = {
            "language": "언어",
            "framework": "프레임워크",
            "database": "데이터베이스",
            "dev_ops": "DevOps",
            "tools": "도구",
            "library": "라이브러리",
            "testing": "테스팅",
            "collaboration": "협업 도구",
        }
        skills = request.skills
        for field_name, label in skill_labels.items():
            skill_list = getattr(skills, field_name, None)
            if skill_list:
                lines.append(f"- {label}: {', '.join(skill_list)}")
        lines.append("")

        # 섹션들
        for section in request.sections:
            lines.append(f"## {section.title}")
            for block in section.blocks:
                lines.append(f"### {block.sub_title} ({block.period})")
                lines.append(f"{block.content}")
                if block.tech_stack:
                    lines.append(f"기술: {', '.join(block.tech_stack)}")
                lines.append("")

        full_text = "\n".join(lines)

        return ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.RESUME_FULL,
            full_resume_text=full_text,
        )

    def assemble_introduction(
        self,
        resume_id: UUID,
        request: ResumeReviewRequest,
    ) -> ReviewContext:
        """소개글 리뷰용 컨텍스트 조립."""
        work_exp_summary = self._preprocess_section(request, SectionType.WORK_EXPERIENCE)
        project_summary = self._preprocess_section(request, SectionType.PROJECT)

        introduction_data = IntroductionData(
            name=request.profile.name,
            position=request.profile.position,
            content=request.profile.introduction,
            work_experience_summary=work_exp_summary,
            project_summary=project_summary,
        )

        return ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.INTRODUCTION,
            introduction=introduction_data,
        )

    def assemble_skill(
        self,
        resume_id: UUID,
        request: ResumeSkillReviewRequest,
    ) -> ReviewContext:
        """스킬 리뷰용 컨텍스트 조립."""
        skill_data = SkillData(
            dev_ops=request.skills.dev_ops,
            language=request.skills.language,
            framework=request.skills.framework,
            database=request.skills.database,
            tools=request.skills.tools,
            library=request.skills.library,
            testing=request.skills.testing,
            collaboration=request.skills.collaboration,
        )

        return ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.SKILL,
            skill=skill_data,
        )

    def assemble_section(
        self,
        resume_id: UUID,
        section_type: SectionType,
        request: ResumeSectionReviewRequest,
    ) -> ReviewContext:
        """섹션 리뷰용 컨텍스트 조립."""

        blocks = [
            BlockData(
                block_id=block.id,
                sub_title=block.sub_title,
                period=block.period,
                content=block.content,
                tech_stack=block.tech_stack,
                link=str(block.link) if block.link else None,
            )
            for block in request.blocks
        ]

        section_data = SectionData(
            section_id=request.id,
            section_type=request.type,
            title=request.title,
            blocks=blocks,
        )

        return ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.from_section_type(section_type),
            section=section_data,
        )

    def assemble_block(
        self,
        resume_id: UUID,
        section_type: SectionType,
        section_id: UUID,
        block_id: UUID,
        request: ResumeBlockReviewRequest,
    ) -> ReviewContext:
        """블록 리뷰용 컨텍스트 조립."""

        block_data = BlockData(
            block_id=request.id,
            sub_title=request.sub_title,
            period=request.period,
            content=request.content,
            tech_stack=request.tech_stack,
            link=str(request.link) if request.link else None,
        )

        return ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.from_section_type_block(section_type),
            block=block_data,
        )

    def _preprocess_section(
        self,
        request: ResumeReviewRequest,
        section_type: SectionType,
    ) -> str:
        """특정 섹션 요약 생성."""
        summaries = []
        for section in request.sections:
            if section.type == section_type:
                for block in section.blocks:
                    summary = f"- {block.sub_title} ({block.period}): {block.content}"
                    summaries.append(summary)
        return "\n".join(summaries) if summaries else "없음"


@lru_cache
def get_review_context_assembler() -> ReviewContextAssembler:
    """ReviewContextAssembler 싱글톤 인스턴스 반환."""
    return ReviewContextAssembler()
