from backend.api.rest.v1.models.resumes import (
    Education,
    Introduction,
    Project,
    TechSkill,
    WorkExperience,
)
from backend.api.rest.v1.schemas.resumes import (
    Block,
    ResumeReviewRequest,
    ResumeSectionReviewRequest,
    ResumeSkillReviewRequest,
)
from backend.utils.enums import ResumeItemType, SectionType


def _get_visible_blocks(
    schema: ResumeReviewRequest | ResumeSectionReviewRequest,
    section_type: SectionType,
) -> list[Block]:
    """Schema에서 특정 SectionType의 visible blocks만 추출하는 헬퍼 함수"""
    if isinstance(schema, ResumeReviewRequest):
        for section in schema.sections:
            if section.type == section_type:
                return [block for block in section.blocks if block.is_visible]
        return []
    elif isinstance(schema, ResumeSectionReviewRequest):
        if schema.type == section_type:
            return [block for block in schema.blocks if block.is_visible]
    return []


class WorkExperienceMapper:
    """경력 변환 매퍼"""

    def to_domain(
        self,
        schema: ResumeReviewRequest | ResumeSectionReviewRequest
    ) -> list[WorkExperience]:
        """ResumeReviewRequest → WorkExperience 리스트 변환"""
        blocks = _get_visible_blocks(schema, SectionType.WORK_EXPERIENCE)

        return [
            WorkExperience(
                company_name=block.sub_title,
                period=block.period,
                tech_stack=block.tech_stack,
                link=block.link,
                content=block.content,
            )
            for block in blocks
        ]


class ProjectMapper:
    """프로젝트 변환 매퍼"""

    def to_domain(
        self,
        schema: ResumeReviewRequest | ResumeSectionReviewRequest
    ) -> list[Project]:
        """ResumeReviewRequest → Project 리스트 변환"""
        blocks = _get_visible_blocks(schema, SectionType.PROJECT)

        return [
            Project(
                project_title=block.sub_title,
                period=block.period,
                tech_stack=block.tech_stack,
                link=block.link,
                content=block.content,
            )
            for block in blocks
        ]


class EducationMapper:
    """교육 변환 매퍼"""

    def to_domain(
        self,
        schema: ResumeReviewRequest | ResumeSectionReviewRequest
    ) -> list[Education]:
        """ResumeReviewRequest → Education 리스트 변환"""
        blocks = _get_visible_blocks(schema, SectionType.EDUCATION)

        if isinstance(schema, ResumeReviewRequest):
            position = schema.profile.position
        else:
            position = "목표 직무 미입력"

        return [
            Education(
                education_name=block.sub_title,
                period=block.period,
                tech_stack=block.tech_stack,
                link=block.link,
                position=position,
                content=block.content,
            )
            for block in blocks
        ]


class IntroductionMapper:
    """
    Introduction 변환 매퍼
    - 여러 섹션(Profile + WorkExperience + Project)을 결합하여 Introduction 도메인 모델로 변환
    """

    def __init__(
        self,
        work_experience_mapper: WorkExperienceMapper,
        project_mapper: ProjectMapper,
    ):
        self._work_experience_mapper = work_experience_mapper
        self._project_mapper = project_mapper

    def to_domain(
        self,
        schema: ResumeReviewRequest
    ) -> Introduction:
        """ResumeReviewRequest → Introduction Aggregate 변환"""
        work_experiences = self._work_experience_mapper.to_domain(schema)
        projects = self._project_mapper.to_domain(schema)

        return Introduction(
            name=schema.profile.name,
            position=schema.profile.position,
            work_experiences=work_experiences,
            projects=projects,
            content=schema.profile.introduction,
        )


class TechSkillMapper:
    """기술 스킬 변환 매퍼"""

    def to_domain(
        self,
        schema: ResumeSkillReviewRequest
    ) -> TechSkill:
        """ResumeSkillReviewRequest → TechSkill 변환"""
        return TechSkill(
            dev_ops=schema.skills.dev_ops,
            language=schema.skills.language,
            framework=schema.skills.framework,
            database=schema.skills.database,
            tools=schema.skills.tools,
            library=schema.skills.library,
            testing=schema.skills.testing,
            collaboration=schema.skills.collaboration,
        )


class ResumeReviewMapperFacade:
    """ResumeReviewRequest → Domain 변환을 위한 Facade

    책임: SectionType에 따라 적절한 Mapper 선택만 담당
    """

    def __init__(self):
        self._work_experience_mapper = WorkExperienceMapper()
        self._project_mapper = ProjectMapper()
        self._education_mapper = EducationMapper()

        self._tech_skill_mapper = TechSkillMapper()
        self._introduction_mapper = IntroductionMapper(
            self._work_experience_mapper,
            self._project_mapper,
        )

    def _validate_item_type(self, item_type: SectionType | ResumeItemType) -> bool:
        """item_type이 지원하는 타입인지 검증"""
        if not any([
            item_type in [ResumeItemType.SKILL, ResumeItemType.INTRODUCTION],
            item_type in [SectionType.WORK_EXPERIENCE, SectionType.PROJECT, SectionType.EDUCATION],
        ]):
            return False
        return True

    def to_section_domain(
        self,
        schema: ResumeReviewRequest | ResumeSectionReviewRequest,
        section_type: SectionType,
    # ) -> list[WorkExperience] | list[Project] | list[Education]:
    ) -> list[WorkExperience | Project | Education]:
        """Schema → Domain 변환 (Section)

        Args:
            schema: 변환할 ResumeSectionReviewRequest
            section_type: 변환할 섹션 타입

        Returns:
            section_type에 따라 적절한 Domain 모델 리스트

        Raises:
            ValueError: 지원하지 않는 section_type인 경우
        """

        if not self._validate_item_type(section_type):
            raise ValueError(f"지원하지 않는 section_type: {section_type}")

        result: list[WorkExperience | Project | Education]
        if section_type == SectionType.WORK_EXPERIENCE:
            result = self._work_experience_mapper.to_domain(schema)
        elif section_type == SectionType.PROJECT:
            result = self._project_mapper.to_domain(schema)
        elif section_type == SectionType.EDUCATION:
            result = self._education_mapper.to_domain(schema)
        else:
            raise ValueError(f"지원하지 않는 section_type: {section_type}")

        return result

    def to_introduction_domain(
        self, 
        schema: ResumeReviewRequest
    ) -> Introduction:
        """소개글 도메인 변환 (ResumeReviewRequest 전용)"""
        result: Introduction = self._introduction_mapper.to_domain(schema)
        return result

    def to_skill_domain(
        self, 
        schema: ResumeSkillReviewRequest
    ) -> TechSkill:
        """기술 스킬 도메인 변환 (ResumeSkillReviewRequest 전용)"""
        result: TechSkill = self._tech_skill_mapper.to_domain(schema)
        return result

