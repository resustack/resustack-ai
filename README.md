# Resustack AI Service

[![CI](https://github.com/hwstar/resustack/actions/workflows/ci.yml/badge.svg)](https://github.com/hwstar/resustack/actions/workflows/ci.yml)
[![Security Scan](https://github.com/hwstar/resustack/actions/workflows/security.yml/badge.svg)](https://github.com/hwstar/resustack/actions/workflows/security.yml)

AI-powered resume review service for Resustack platform. 이력서의 다양한 부분(소개글, 스킬, 경력, 프로젝트, 교육)을 AI로 평가하고 개선안을 제시하는 서비스입니다.

## Features

- **2단계 AI 리뷰 프로세스**: 평가(Evaluation) → 개선(Improvement)
- **세분화된 리뷰 타입**: 소개글, 스킬, 섹션(경력/프로젝트/교육), 블록 단위 리뷰
- **Strategy 패턴 기반 프롬프트 관리**: 리뷰 타입별 최적화된 프롬프트 전략
- **YAML 기반 프롬프트 템플릿**: 코드와 프롬프트 분리로 유지보수성 향상
- **구조화된 AI 출력**: Pydantic 모델을 통한 타입 안전한 응답
- **LangChain 기반 AI 파이프라인**: Anthropic Claude 4.5 haiku 활용
- **RESTful API**: FastAPI 기반 camelCase 자동 변환 지원

## Tech Stack

- **Framework**: FastAPI
- **AI/LLM**: LangChain, LangChain-Anthropic
- **Security**: python-jose, passlib
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: ruff, mypy, pre-commit

## Setup

### Prerequisites

- Python 3.12+
- UV package manager

### Installation

1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API keys
4. Install dependencies:
   ```bash
   uv sync
   ```

### Development

Run the development server:
```bash
uv run uvicorn backend.main:app --reload
```

Run tests:
```bash
uv run pytest
```

Format code:
```bash
uv run ruff format backend tests
```

Lint code:
```bash
uv run ruff check backend tests
```

Type check:
```bash
uv run mypy backend
```

### Environment Variables

`.env` 파일에 다음 변수들을 설정해야 합니다:

```env
# Anthropic API
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # 선택사항 (기본값)
ANTHROPIC_MAX_TOKENS=4096  # 선택사항 (기본값)
ANTHROPIC_TEMPERATURE=0.7  # 선택사항 (기본값)
```

## 주요 기능 상세

### 2단계 리뷰 프로세스

모든 리뷰는 2단계로 진행됩니다:

1. **평가 단계 (Evaluation)**
   - 내용을 분석하여 강점과 약점을 파악
   - `EvaluationResult` 반환

2. **개선 단계 (Improvement)**
   - 평가 결과를 바탕으로 구체적인 개선안 생성
   - 개선된 내용 제안 (`improved_content`)
   - 최종 `ReviewResult` 반환

### 프롬프트 관리

- **YAML 템플릿**: `backend/ai/prompts/templates/`에 프롬프트 저장
- **전략 패턴**: 리뷰 타입별로 최적화된 프롬프트 전략 사용
- **캐싱**: YAML 로더에 LRU 캐시 적용

### 타입 안전성

- **Pydantic 모델**: 모든 요청/응답 검증
- **구조화된 AI 출력**: `PydanticOutputParser`로 AI 응답 파싱
- **타입 힌팅**: MyPy로 정적 타입 검사

## 개발 가이드

### 새로운 리뷰 타입 추가하기

1. `backend/services/review/enums.py`에 `ReviewTargetType` 추가
2. `backend/ai/prompts/`에 새로운 Strategy 클래스 생성
3. `backend/ai/strategies/factory.py`에 전략 등록
4. `backend/ai/prompts/templates/`에 YAML 프롬프트 템플릿 추가
5. `backend/services/review/assembler.py`에 컨텍스트 조립 로직 추가
6. `backend/api/rest/v1/routes/reviews.py`에 엔드포인트 추가

## Project Structure

```
resustack/
├── backend/                    # Backend source code
│   ├── api/                    # API interface layer
│   │   └── rest/               # RESTful API (FastAPI)
│   │       ├── v1/             # API v1
│   │       │   ├── routes/     # v1 route handlers
│   │       │   │   └── reviews.py  # 리뷰 엔드포인트
│   │       │   └── schemas/    # v1 request/response models
│   │       │       ├── resumes.py  # 요청 스키마
│   │       │       └── reviews.py  # 응답 스키마
│   │       ├── main.py         # FastAPI app initialization
│   │       └── exceptions.py    # 예외 핸들러
│   ├── ai/                     # AI/LLM layer
│   │   ├── chains/             # LangChain chains
│   │   │   ├── llm.py          # Anthropic 클라이언트
│   │   │   └── review_chain.py # 2단계 리뷰 체인
│   │   ├── strategies/         # 프롬프트 전략 패턴
│   │   │   ├── base.py         # 기본 전략
│   │   │   └── factory.py      # 전략 팩토리
│   │   ├── prompts/            # 프롬프트 전략 구현
│   │   │   ├── introduction.py # 소개글 전략
│   │   │   ├── skill.py        # 스킬 전략
│   │   │   ├── section.py      # 섹션 전략
│   │   │   ├── block.py        # 블록 전략
│   │   │   └── templates/      # YAML 프롬프트 템플릿
│   │   ├── output/             # AI 출력 스키마
│   │   │   └── review_result.py
│   │   └── config.py           # AI 설정
│   ├── services/               # Business logic layer
│   │   └── review/             # 리뷰 서비스
│   │       ├── service.py      # ReviewService
│   │       ├── assembler.py    # ReviewContext 조립
│   │       ├── mapper.py       # 응답 변환
│   │       ├── context.py     # ReviewContext 모델
│   │       └── enums.py        # ReviewTargetType
│   ├── domain/                 # Domain models
│   │   └── resume/             # 이력서 도메인
│   │       ├── models.py      # Resume, Profile, Section, Block, Skills
│   │       └── enums.py       # SectionType, ResumeItemType
│   ├── utils/                  # Utility functions
│   │   ├── yaml_loader.py     # YAML 프롬프트 로더
│   │   └── schema_base.py     # CamelCase 변환 유틸
│   └── main.py                 # Application entry point
├── tests/                      # Test files
│   ├── conftest.py             # Pytest configuration
│   └── test_main.py            # API tests
├── .env.example                # Environment template
├── .python-version             # Python version specification
└── pyproject.toml              # Project configuration
```

### Architecture Design

이 프로젝트는 **확장 가능한 레이어드 아키텍처**를 따릅니다:

#### 레이어 구조

```
┌─────────────────────────────────────┐
│      API Layer (FastAPI)            │
│  - 요청/응답 검증 및 직렬화              │
│  - 예외 처리                          │
│  - camelCase 자동 변환                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼────────────────────────┐
│    Services Layer                     │
│  - ReviewService: 비즈니스 로직          │
│  - ReviewContextAssembler: 컨텍스트 조립 │
│  - ReviewResponseMapper: 응답 변환      │
└──────────────┬────────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      AI Layer (LangChain)           │
│  - ReviewChain: 2단계 리뷰 프로세스     │
│  - PromptStrategy: 타입별 프롬프트      │
│  - 구조화된 출력 (Pydantic)            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Domain Layer                     │
│  - Resume, Profile, Section, Block  │
│  - SectionType, ReviewTargetType    │
└─────────────────────────────────────┘
```

#### 데이터 흐름

1. **API Request** (camelCase JSON)
   - FastAPI가 자동으로 snake_case로 변환
   - Pydantic으로 요청 검증

2. **ReviewContextAssembler**
   - Request Schema → ReviewContext 변환
   - 리뷰 타입에 맞는 컨텍스트 조립

3. **PromptStrategyFactory**
   - ReviewTargetType에 따라 적절한 Strategy 선택
   - IntroductionPromptStrategy, SkillPromptStrategy 등

4. **ReviewChain (2단계 프로세스)**
   - **Step 1: Evaluation** - 강점/약점 분석
   - **Step 2: Improvement** - 평가 결과 기반 개선안 생성

5. **ReviewResponseMapper**
   - AI 출력 (ReviewResult) → API Response 변환
   - camelCase로 자동 변환

#### 주요 설계 패턴

- **Strategy Pattern**: 리뷰 타입별 프롬프트 전략 분리
- **Factory Pattern**: PromptStrategyFactory로 전략 생성
- **Chain of Responsibility**: 2단계 리뷰 체인
- **Mapper Pattern**: 도메인 모델 ↔ API 모델 변환

## API Endpoints

### v1

#### 공통
- `GET /` - Service status
- `GET /health` - Health check

#### 리뷰 엔드포인트

모든 리뷰 엔드포인트는 `POST /api/v1/resumes/{resume_id}/reviews/...` 형식을 따릅니다.

##### 소개글 리뷰
```
POST /api/v1/resumes/{resume_id}/reviews/introduction
```
- 이력서 소개글을 평가하고 개선안을 제시합니다.
- 핵심 역량 명확성, 차별화 포인트, 직무 연관성 등을 평가합니다.

##### 스킬 리뷰
```
POST /api/v1/resumes/{resume_id}/reviews/skills
```
- 기술 스택을 평가하고 추가/제거할 기술을 제안합니다.
- 기술 스택 구성, 깊이 vs 넓이, 최신 트렌드 반영 등을 평가합니다.

##### 섹션 리뷰
```
POST /api/v1/resumes/{resume_id}/reviews/sections/{section_type}/{section_id}
```
- 특정 섹션(경력/프로젝트/교육)의 모든 블록을 평가합니다.
- 섹션 내 모든 블록을 순회하며 개별 평가 후 종합 결과를 반환합니다.
- `section_type`: `work_experience`, `project`, `education`

##### 블록 리뷰
```
POST /api/v1/resumes/{resume_id}/reviews/sections/{section_type}/{section_id}/blocks/{block_id}
```
- 섹션 내 특정 블록 하나만 선택하여 상세 평가합니다.
- 예: 여러 프로젝트 중 하나의 프로젝트만 리뷰

##### 전체 이력서 요약 리뷰
```
POST /api/v1/resumes/{resume_id}/reviews/summary
```
- 이력서 전체를 종합적으로 평가하고 개선 방향을 제시합니다.
- 전체 구성, 일관성, 차별화 포인트 등을 평가합니다.

### 응답 형식

모든 리뷰 응답은 다음 구조를 따릅니다:

```json
{
  "resumeId": "uuid",
  "targetType": "introduction|skill|work_experience|...",
  "evaluationSummary": "전반적인 평가 요약",
  "strengths": ["강점1", "강점2"],
  "weaknesses": [
    {
      "problem": "구체적인 문제점",
      "reason": "왜 문제인지 설명"
    }
  ],
  "improvementSuggestion": "개선 제안 요약",
  "improvedContent": "개선된 문장/내용 (블록/아이템 리뷰 시)",
  "blockId": "uuid (블록 리뷰 시)"
}
```

섹션 리뷰의 경우 추가로 `overallEvaluation`과 `blockResults` 배열이 포함됩니다.

## CI/CD

이 프로젝트는 GitHub Actions를 사용한 자동화된 CI/CD 파이프라인을 제공합니다.

### 워크플로우

#### 1. CI (Continuous Integration)
- **트리거**: `main`, `develop` 브랜치에 push 또는 PR
- **작업**:
  - 코드 린팅 (Ruff)
  - 포매팅 체크
  - 타입 체크 (MyPy)
  - 단위/통합 테스트 실행
  - Docker 이미지 빌드 테스트

#### 2. PR Check
- **트리거**: Pull Request 생성/업데이트
- **작업**:
  - 린트 및 테스트 실행
  - PR에 자동으로 테스트 결과 코멘트

#### 3. Security Scan
- **트리거**: Push, PR, 매주 월요일 자동 실행
- **작업**:
  - 의존성 보안 검사
  - Trivy 취약점 스캔 (파일시스템 + Docker 이미지)
  - GitHub Security 탭에 결과 업로드

#### 4. CD (Continuous Deployment)
- **트리거**: `main` 브랜치 push 또는 버전 태그 (`v*.*.*`)
- **작업**:
  - Docker 이미지 빌드
  - GitHub Container Registry에 푸시
  - 이미지 attestation 생성

### 배포 프로세스

#### 개발 환경
```bash
# develop 브랜치에 push하면 자동으로 CI 실행
git push origin develop
```

#### 프로덕션 배포
```bash
# 1. 버전 태그 생성
git tag v1.0.0
git push origin v1.0.0

# 2. GitHub Container Registry에서 이미지 pull
docker pull ghcr.io/hwstar/resustack:v1.0.0

# 3. 이미지 실행
docker run -p 8000:8000 --env-file .env ghcr.io/hwstar/resustack:v1.0.0
```

### Dependabot

자동 의존성 업데이트를 위해 Dependabot이 설정되어 있습니다:
- GitHub Actions 주간 업데이트
- Python 패키지 주간 업데이트
- Docker 베이스 이미지 주간 업데이트
