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
uv run uvicorn src.app.main:app --reload
```

Run tests:
```bash
uv run pytest
```

Format code:
```bash
uv run ruff format src tests
```

Lint code:
```bash
uv run ruff check src tests
```

Type check:
```bash
uv run mypy src
```

## Project Structure

```
resustack/
├── src/
│   ├── app/          # FastAPI application
│   ├── core/         # Configuration and security
│   ├── services/     # AI service logic
│   ├── models/       # Pydantic models
│   └── utils/        # Utility functions
├── tests/            # Test files
├── .env.example      # Environment template
└── pyproject.toml    # Project configuration
```

## API Endpoints

- `GET /` - Service status
- `GET /health` - Health check

## License

MIT
