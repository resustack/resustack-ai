# Resustack AI Service

AI-powered resume review and JD matching service for Resustack platform.

## Features

- AI resume review using LangChain and Anthropic
- Job Description (JD) matching analysis
- Token counting and cost management
- JWT-based authentication
- RESTful API with FastAPI

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

## Project Structure

```
resustack/
├── backend/                    # Backend source code
│   ├── api/                    # API interface layer
│   │   └── rest/               # RESTful API (FastAPI)
│   │       ├── v1/             # API v1
│   │       │   ├── routes/     # v1 route handlers
│   │       │   └── models/     # v1 request/response models
│   │       └── main.py         # FastAPI app initialization
│   │   └── gRPC/               # (future)
│   ├── ai/                     # AI/LLM layer (LangChain, LangGraph)
│   │   ├── chains/             # LangChain chains for complex AI workflows
│   │   ├── models/             # AI model configurations and wrappers
│   │   ├── prompts/            # Prompt templates and management
│   │   └── config.py           # AI configuration
│   ├── services/               # Business logic layer
│   ├── utils/                  # Utility functions
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

- **API Layer** (`backend/api/`): REST API 인터페이스 (향후 GraphQL, gRPC 추가 가능)
  - 버전 관리 지원 (v1, v2, ...)
  - 요청/응답 검증 및 직렬화

- **Services Layer** (`backend/services/`): 비즈니스 로직
  - 도메인별 서비스 구성 (resume, jd 등)
  - API와 AI 레이어 사이의 중재자 역할

- **AI Layer** (`backend/ai/`): AI/LLM 관련 로직
  - LangChain chains, LangGraph agents
  - 프롬프트 관리 및 AI 모델 설정
  - AI 구조화 출력 스키마

## API Endpoints

### v1
- `GET /` - Service status
- `GET /health` - Health check
