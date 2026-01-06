from uuid import UUID

from backend.api.rest.v1.mapper import ResumeReviewMapperFacade
from backend.api.rest.v1.models.resumes import AIReviewResult
from backend.api.rest.v1.schemas.resumes import (
    ResumeReviewRequest,
    ResumeSectionReviewRequest,
    ResumeSkillReviewRequest,
)
from backend.utils.enums import ResumeItemType, SectionType


class ResumeReviewService:
    """
    이력서 리뷰 서비스

    서비스 종류
    - 이력서 전체 리뷰
    - 소개글, 경력, 프로젝트, 교육 리뷰

    로직 순서
    1. Request → Domain (API 계층)
    2. Domain → AI Input (AI 계층)
    3. AI 호출
    4. AI Output → Domain (AI 계층)
    5. 영속성 (Repository) (추후 고려 사항)
    6. Domain → Response (API 계층)
    """

    def __init__(
        self,
        item_type: SectionType | ResumeItemType | None = None,
        item_id: UUID | None = None,
    ):
        self.item_type = item_type
        self.item_id = item_id
        self.facade = ResumeReviewMapperFacade()

    async def review_resume_all(
        self,
        resume_id: UUID,
        request: ResumeReviewRequest,
    ) -> AIReviewResult:
        """
        이력서 전체 리뷰

        Args:
            request: 이력서 리뷰 요청 데이터

        Returns:
            AIReviewResult: 평가 결과 및 개선 제안
        """

        introduction_domain = self.facade.to_introduction_domain(request)
        skill_request = ResumeSkillReviewRequest(skills=request.skills)
        skill_domain = self.facade.to_skill_domain(skill_request)

        work_experience_domain = self.facade.to_section_domain(
            request,
            SectionType.WORK_EXPERIENCE,
        )
        project_domain = self.facade.to_section_domain(
            request,
            SectionType.PROJECT,
        )
        education_domain = self.facade.to_section_domain(
            request,
            SectionType.EDUCATION,
        )

        # TODO: AI 호출 로직 구현 (이력서 전체 리뷰)

        print(f"""
            introduction_domain: {introduction_domain}
            skill_domain: {skill_domain}
            work_experience_domain: {work_experience_domain}
            project_domain: {project_domain}
            education_domain: {education_domain}
        """)

        return AIReviewResult(
            resume_id=resume_id,
            evaluation_result="evaluation result",
            improvement_suggestion="improvement suggestion",
            improved_resume_blocks_content=[],
        )

    async def review_resume_section(
        self,
        resume_id: UUID,
        request: ResumeSectionReviewRequest,
    ) -> AIReviewResult:
        """
        이력서 섹션 리뷰

        Args:
            request: 이력서 섹션 리뷰 요청 데이터

        Returns:
            AIReviewResult: 평가 결과 및 개선 제안
        """

        if not isinstance(self.item_type, SectionType):
            raise ValueError(f"지원하지 않는 item_type: {self.item_type}")
        domain = self.facade.to_section_domain(request, self.item_type)

        # TODO: AI 호출 로직 구현 (섹션 리뷰)
        print(f"domain: {domain}")

        return AIReviewResult(
            resume_id=resume_id,
            evaluation_result="evaluation result",
            improvement_suggestion="improvement suggestion",
            improved_resume_blocks_content=[],
        )

    async def review_resume_introduction(
        self,
        resume_id: UUID,
        request: ResumeReviewRequest,
    ) -> AIReviewResult:
        """
        소개글 리뷰

        Args:
            request: 소개글 리뷰 요청 데이터

        Returns:
            AIReviewResult: 리뷰 결과 및 개선 제안
        """
        introduction_domain = self.facade.to_introduction_domain(request)

        # TODO: AI 호출 로직 구현 (소개글 리뷰)

        print(f"introduction_domain: {introduction_domain}")

        return AIReviewResult(
            resume_id=resume_id,
            evaluation_result="evaluation result",
            improvement_suggestion="improvement suggestion",
            improved_resume_blocks_content=[],
        )

    async def review_resume_skill(
        self,
        resume_id: UUID,
        request: ResumeSkillReviewRequest
    ) -> AIReviewResult:
        """
        스킬 리뷰

        Args:
            request: 스킬 리뷰 요청 데이터

        Returns:
            AIReviewResult: 리뷰 결과 및 개선 제안
        """

        skill_domain = self.facade.to_skill_domain(request)

        # TODO: AI 호출 로직 구현 (스킬 리뷰)

        print(f"skill_domain: {skill_domain}")

        return AIReviewResult(
            resume_id=resume_id,
            evaluation_result="evaluation result",
            improvement_suggestion="improvement suggestion",
            improved_resume_blocks_content=[],
        )
