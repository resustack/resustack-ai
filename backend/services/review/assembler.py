"""Review Context Assembler.

Request Schema를 해석하여 ReviewContext 도메인 모델로 조립합니다.
"""

from uuid import UUID

from backend.api.rest.v1.schemas.resumes import (
    Block,
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
        full_text = self._build_full_resume_text(request)

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
        work_exp_summary = self._summarize_section(
            request, SectionType.WORK_EXPERIENCE
        )
        project_summary = self._summarize_section(request, SectionType.PROJECT)

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
        section_data = self._build_section_data(request)

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
        block_data = self._build_block_data_from_request(request)

        return ReviewContext(
            resume_id=resume_id,
            target_type=ReviewTargetType.from_section_type_block(section_type),
            block=block_data,
        )

    def _build_full_resume_text(self, request: ResumeReviewRequest) -> str:
        """전체 이력서를 텍스트로 변환."""
        lines = []

        lines.append("## 프로필")
        lines.append(f"- 이름: {request.profile.name}")
        lines.append(f"- 직무: {request.profile.position}")
        lines.append(f"- 소개글: {request.profile.introduction}")
        lines.append("")

        lines.append("## 스킬")
        skills = request.skills
        if skills.language:
            lines.append(f"- 언어: {', '.join(skills.language)}")
        if skills.framework:
            lines.append(f"- 프레임워크: {', '.join(skills.framework)}")
        if skills.database:
            lines.append(f"- 데이터베이스: {', '.join(skills.database)}")
        if skills.dev_ops:
            lines.append(f"- DevOps: {', '.join(skills.dev_ops)}")
        lines.append("")

        for section in request.sections:
            lines.append(f"## {section.title}")
            for block in section.blocks:
                if block.is_visible:
                    lines.append(f"### {block.sub_title} ({block.period})")
                    lines.append(f"{block.content}")
                    if block.tech_stack:
                        lines.append(f"기술: {', '.join(block.tech_stack)}")
                    lines.append("")

        return "\n".join(lines)

    def _summarize_section(
        self,
        request: ResumeReviewRequest,
        section_type: SectionType,
    ) -> str:
        """특정 섹션 요약 생성."""
        for section in request.sections:
            if section.type == section_type:
                summaries = []
                for block in section.blocks:
                    if block.is_visible:
                        content = block.content
                        summary = (
                            f"- {block.sub_title} ({block.period}): {content[:100]}..."
                            if len(content) > 100
                            else f"- {block.sub_title} ({block.period}): {content}"
                        )
                        summaries.append(summary)
                return "\n".join(summaries) if summaries else "없음"
        return "없음"

    def _build_section_data(self, request: ResumeSectionReviewRequest) -> SectionData:
        """ResumeSectionReviewRequest → SectionData 변환."""
        blocks = [
            self._build_block_data_from_block(block)
            for block in request.blocks
            if block.is_visible
        ]

        return SectionData(
            section_id=request.id,
            section_type=request.type,
            title=request.title,
            blocks=blocks,
        )

    def _build_block_data_from_request(self, request: ResumeBlockReviewRequest) -> BlockData:
        """ResumeBlockReviewRequest → BlockData 변환."""
        return BlockData(
            block_id=request.id,
            sub_title=request.sub_title,
            period=request.period,
            content=request.content,
            tech_stack=request.tech_stack,
            link=str(request.link) if request.link else None,
        )

    def _build_block_data_from_block(self, block: Block) -> BlockData:
        """Block → BlockData 변환."""
        return BlockData(
            block_id=block.id,
            sub_title=block.sub_title,
            period=block.period,
            content=block.content,
            tech_stack=block.tech_stack,
            link=str(block.link) if block.link else None,
        )
