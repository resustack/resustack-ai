"""PromptStrategyFactory 테스트."""

from uuid import uuid4

import pytest
from backend.ai.prompts.block import BlockPromptStrategy
from backend.ai.prompts.full_resume import FullResumePromptStrategy
from backend.ai.prompts.introduction import IntroductionPromptStrategy
from backend.ai.prompts.section import SectionPromptStrategy
from backend.ai.prompts.skill import SkillPromptStrategy
from backend.ai.strategies.factory import PromptStrategyFactory
from backend.domain.resume.enums import SectionType
from backend.services.review.context import (
    BlockData,
    IntroductionData,
    ReviewContext,
    SectionData,
    SkillData,
)
from backend.services.review.enums import ReviewTargetType


class TestPromptStrategyFactoryResumeFull:
    """전체 이력서 전략 테스트."""

    def test_get_full_resume_strategy(self) -> None:
        """RESUME_FULL 타입에 대해 FullResumePromptStrategy 반환."""
        context = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.RESUME_FULL,
            full_resume_text="전체 이력서 텍스트",
        )

        strategy = PromptStrategyFactory.get(context)

        assert isinstance(strategy, FullResumePromptStrategy)


class TestPromptStrategyFactoryIntroduction:
    """소개글 전략 테스트."""

    def test_get_introduction_strategy(self) -> None:
        """INTRODUCTION 타입에 대해 IntroductionPromptStrategy 반환."""
        context = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.INTRODUCTION,
            introduction=IntroductionData(
                name="홍길동",
                position="백엔드 개발자",
                content="소개글입니다",
            ),
        )

        strategy = PromptStrategyFactory.get(context)

        assert isinstance(strategy, IntroductionPromptStrategy)


class TestPromptStrategyFactorySkill:
    """스킬 전략 테스트."""

    def test_get_skill_strategy(self) -> None:
        """SKILL 타입에 대해 SkillPromptStrategy 반환."""
        context = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.SKILL,
            skill=SkillData(
                language=["Python", "TypeScript"],
                framework=["FastAPI", "React"],
            ),
        )

        strategy = PromptStrategyFactory.get(context)

        assert isinstance(strategy, SkillPromptStrategy)


class TestPromptStrategyFactorySection:
    """섹션 전략 테스트."""

    @pytest.fixture
    def sample_section_data(self) -> SectionData:
        """샘플 SectionData."""
        return SectionData(
            section_id=uuid4(),
            section_type=SectionType.PROJECT,
            title="프로젝트",
            blocks=[
                BlockData(
                    block_id=uuid4(),
                    sub_title="프로젝트 1",
                    period="2023.01 - 2023.12",
                    content="프로젝트 내용",
                )
            ],
        )

    def test_get_work_experience_section_strategy(self, sample_section_data: SectionData) -> None:
        """WORK_EXPERIENCE 타입에 대해 SectionPromptStrategy 반환."""
        sample_section_data.section_type = SectionType.WORK_EXPERIENCE
        context = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.WORK_EXPERIENCE,
            section=sample_section_data,
        )

        strategy = PromptStrategyFactory.get(context)

        assert isinstance(strategy, SectionPromptStrategy)

    def test_get_project_section_strategy(self, sample_section_data: SectionData) -> None:
        """PROJECT 타입에 대해 SectionPromptStrategy 반환."""
        context = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.PROJECT,
            section=sample_section_data,
        )

        strategy = PromptStrategyFactory.get(context)

        assert isinstance(strategy, SectionPromptStrategy)

    def test_get_education_section_strategy(self, sample_section_data: SectionData) -> None:
        """EDUCATION 타입에 대해 SectionPromptStrategy 반환."""
        sample_section_data.section_type = SectionType.EDUCATION
        context = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.EDUCATION,
            section=sample_section_data,
        )

        strategy = PromptStrategyFactory.get(context)

        assert isinstance(strategy, SectionPromptStrategy)


class TestPromptStrategyFactoryBlock:
    """블록 전략 테스트."""

    @pytest.fixture
    def sample_block_data(self) -> BlockData:
        """샘플 BlockData."""
        return BlockData(
            block_id=uuid4(),
            sub_title="AI 챗봇 서비스",
            period="2023.01 - 2023.12",
            content="FastAPI 기반 챗봇 백엔드 구축",
            tech_stack=["Python", "FastAPI"],
        )

    def test_get_work_experience_block_strategy(self, sample_block_data: BlockData) -> None:
        """WORK_EXPERIENCE_BLOCK 타입에 대해 BlockPromptStrategy 반환."""
        context = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.WORK_EXPERIENCE_BLOCK,
            block=sample_block_data,
        )

        strategy = PromptStrategyFactory.get(context)

        assert isinstance(strategy, BlockPromptStrategy)

    def test_get_project_block_strategy(self, sample_block_data: BlockData) -> None:
        """PROJECT_BLOCK 타입에 대해 BlockPromptStrategy 반환."""
        context = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.PROJECT_BLOCK,
            block=sample_block_data,
        )

        strategy = PromptStrategyFactory.get(context)

        assert isinstance(strategy, BlockPromptStrategy)

    def test_get_education_block_strategy(self, sample_block_data: BlockData) -> None:
        """EDUCATION_BLOCK 타입에 대해 BlockPromptStrategy 반환."""
        context = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.EDUCATION_BLOCK,
            block=sample_block_data,
        )

        strategy = PromptStrategyFactory.get(context)

        assert isinstance(strategy, BlockPromptStrategy)


class TestPromptStrategyFactoryAllTypes:
    """모든 타입에 대한 전략 반환 테스트."""

    @pytest.mark.parametrize(
        "target_type,expected_strategy_type",
        [
            (ReviewTargetType.RESUME_FULL, FullResumePromptStrategy),
            (ReviewTargetType.INTRODUCTION, IntroductionPromptStrategy),
            (ReviewTargetType.SKILL, SkillPromptStrategy),
            (ReviewTargetType.WORK_EXPERIENCE, SectionPromptStrategy),
            (ReviewTargetType.PROJECT, SectionPromptStrategy),
            (ReviewTargetType.EDUCATION, SectionPromptStrategy),
            (ReviewTargetType.WORK_EXPERIENCE_BLOCK, BlockPromptStrategy),
            (ReviewTargetType.PROJECT_BLOCK, BlockPromptStrategy),
            (ReviewTargetType.EDUCATION_BLOCK, BlockPromptStrategy),
        ],
    )
    def test_all_target_types_return_correct_strategy(
        self, target_type: ReviewTargetType, expected_strategy_type: type
    ) -> None:
        """모든 target_type에 대해 올바른 전략이 반환되는지 확인."""
        # 각 타입에 맞는 최소한의 데이터 설정
        context_data = {"resume_id": uuid4(), "target_type": target_type}

        if target_type == ReviewTargetType.RESUME_FULL:
            context_data["full_resume_text"] = "텍스트"
        elif target_type == ReviewTargetType.INTRODUCTION:
            context_data["introduction"] = IntroductionData(
                name="테스트", position="개발자", content="내용"
            )
        elif target_type == ReviewTargetType.SKILL:
            context_data["skill"] = SkillData()
        elif target_type in [
            ReviewTargetType.WORK_EXPERIENCE,
            ReviewTargetType.PROJECT,
            ReviewTargetType.EDUCATION,
        ]:
            context_data["section"] = SectionData(
                section_id=uuid4(),
                section_type=SectionType.PROJECT,
                title="섹션",
            )
        else:  # Block types
            context_data["block"] = BlockData(
                block_id=uuid4(),
                sub_title="블록",
                period="2023",
                content="내용",
            )

        context = ReviewContext(**context_data)
        strategy = PromptStrategyFactory.get(context)

        assert isinstance(strategy, expected_strategy_type)


class TestPromptStrategyFactoryEdgeCases:
    """엣지 케이스 테스트."""

    def test_strategy_is_new_instance_each_time(self) -> None:
        """매번 새로운 전략 인스턴스가 생성되는지 확인."""
        context = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.INTRODUCTION,
            introduction=IntroductionData(name="테스트", position="개발자", content="내용"),
        )

        strategy1 = PromptStrategyFactory.get(context)
        strategy2 = PromptStrategyFactory.get(context)

        # 매번 새로운 인스턴스가 생성됨
        assert strategy1 is not strategy2
        assert type(strategy1) is type(strategy2)

    def test_different_contexts_same_type(self) -> None:
        """같은 타입의 다른 컨텍스트에 대해 동일한 전략 타입 반환."""
        context1 = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.PROJECT_BLOCK,
            block=BlockData(
                block_id=uuid4(),
                sub_title="프로젝트 A",
                period="2023.01",
                content="내용 A",
            ),
        )
        context2 = ReviewContext(
            resume_id=uuid4(),
            target_type=ReviewTargetType.PROJECT_BLOCK,
            block=BlockData(
                block_id=uuid4(),
                sub_title="프로젝트 B",
                period="2023.06",
                content="내용 B",
            ),
        )

        strategy1 = PromptStrategyFactory.get(context1)
        strategy2 = PromptStrategyFactory.get(context2)

        assert type(strategy1) is type(strategy2)
        assert isinstance(strategy1, BlockPromptStrategy)
        assert isinstance(strategy2, BlockPromptStrategy)
