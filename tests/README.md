# 테스트 가이드

이 문서는 Resustack AI Service 프로젝트의 테스트 작성 및 실행 가이드입니다.

## 테스트 구조

```
tests/
├── conftest.py              # 공통 fixtures
├── test_main.py             # 메인 엔드포인트 테스트
├── domain/                  # 도메인 모델 테스트
│   └── test_resume_models.py
├── api/                     # API 엔드포인트 테스트
│   └── test_review_endpoints.py
├── services/                # 서비스 레이어 테스트
│   └── test_review_service.py
├── utils/                   # 유틸리티 함수 테스트
│   └── test_yaml_loader.py
└── integration/             # 통합 테스트
    └── test_review_flow.py
```

## 테스트 실행

### 전체 테스트 실행
```bash
uv run pytest
```

### 특정 디렉토리 테스트
```bash
uv run pytest tests/domain/
uv run pytest tests/api/
uv run pytest tests/services/
```

### 특정 파일 테스트
```bash
uv run pytest tests/domain/test_resume_models.py
```

### 특정 테스트 클래스 또는 함수
```bash
# 클래스
uv run pytest tests/domain/test_resume_models.py::TestProfile

# 함수
uv run pytest tests/domain/test_resume_models.py::TestProfile::test_profile_creation_success
```

### 키워드로 필터링
```bash
# "profile"이 포함된 테스트만 실행
uv run pytest -k profile

# "success"가 포함된 테스트만 실행
uv run pytest -k success
```

### 상세 출력
```bash
# verbose 모드
uv run pytest -v

# 출력 표시 (print문 확인)
uv run pytest -s

# 둘 다
uv run pytest -v -s
```

### 실패한 테스트만 재실행
```bash
uv run pytest --lf
```

### 커버리지 측정
```bash
# 커버리지 포함 실행
uv run pytest --cov=backend

# HTML 리포트 생성
uv run pytest --cov=backend --cov-report=html

# 커버리지가 낮은 파일 확인
uv run pytest --cov=backend --cov-report=term-missing
```

## 테스트 작성 가이드

### 1. 도메인 모델 테스트

도메인 모델의 생성, 검증, 변환을 테스트합니다.

**테스트 대상:**
- Pydantic 모델 생성 및 검증
- field_validator 동작
- alias 처리 (camelCase ↔ snake_case)
- 길이 제한, 범위 제한 등

**예시:**
```python
def test_profile_creation_success(self) -> None:
    """정상적인 Profile 생성."""
    profile = Profile(
        name="홍길동",
        position="백엔드 개발자",
        introduction="FastAPI 전문가",
        email="hong@example.com",
        phone="010-1234-5678",
    )
    assert profile.name == "홍길동"
```

### 2. API 엔드포인트 테스트

FastAPI 엔드포인트의 요청/응답을 테스트합니다.

**테스트 대상:**
- 정상 요청 처리
- 잘못된 요청 검증 (422 Validation Error)
- 응답 스키마 확인
- 의존성 모킹 (Dependency Injection)

**예시:**
```python
@pytest.mark.asyncio
async def test_review_introduction_success(
    self, client: TestClient, mock_review_service: MagicMock
) -> None:
    """소개글 리뷰 성공."""
    resume_id = uuid4()

    mock_response = ReviewResponse(...)
    mock_review_service.review_introduction = AsyncMock(return_value=mock_response)

    response = client.post(f"/api/v1/resumes/{resume_id}/reviews/introduction", json={...})

    assert response.status_code == 200
    assert response.json()["targetType"] == "introduction"
```

### 3. 서비스 레이어 테스트

비즈니스 로직을 테스트합니다.

**테스트 대상:**
- 서비스 메서드 동작
- 외부 의존성 모킹 (AI 체인, DB 등)
- 예외 처리
- 데이터 변환 및 가공

**예시:**
```python
@pytest.mark.asyncio
async def test_review_summary_success(
    self,
    review_service: ReviewService,
    mock_assembler: MagicMock,
    mock_chain: MagicMock,
) -> None:
    """전체 이력서 리뷰 성공."""
    mock_chain.run.return_value = mock_result

    await review_service.review_summary(resume_id, request)

    mock_chain.run.assert_called_once()
```

### 4. 통합 테스트

여러 레이어를 통합하여 전체 플로우를 테스트합니다.

**테스트 대상:**
- API → 서비스 → AI 체인 전체 플로우
- 에러 전파 및 처리
- 데이터 흐름 검증

**예시:**
```python
@pytest.mark.asyncio
async def test_introduction_review_full_flow(
    self, client: TestClient, mock_ai_chain
) -> None:
    """소개글 리뷰 전체 플로우 테스트."""
    # AI 체인 모킹
    mock_ai_chain.run.return_value = mock_result

    # API 호출
    response = client.post(...)

    # 검증
    assert response.status_code == 200
    assert mock_ai_chain.run.called
```

### 5. 유틸리티 함수 테스트

공통 유틸리티 함수의 동작을 테스트합니다.

**테스트 대상:**
- 순수 함수 입출력
- 캐싱 동작
- 예외 처리

## Fixtures 활용

`conftest.py`에 정의된 공통 fixtures를 활용하세요.

**사용 가능한 fixtures:**
- `client`: FastAPI TestClient
- `sample_profile`: 샘플 Profile 데이터
- `sample_skills`: 샘플 Skills 데이터
- `sample_block`: 샘플 Block 데이터
- `sample_section`: 샘플 Section 데이터
- `sample_resume`: 샘플 Resume 데이터

**사용 예시:**
```python
def test_with_sample_data(sample_profile: Profile, sample_skills: Skills) -> None:
    """샘플 데이터를 활용한 테스트."""
    assert sample_profile.name == "홍길동"
    assert len(sample_skills.language) > 0
```

## 모킹 (Mocking)

### 1. AsyncMock 사용

비동기 함수는 `AsyncMock`을 사용합니다.

```python
from unittest.mock import AsyncMock

mock_chain.run = AsyncMock(return_value=mock_result)
await mock_chain.run(context)
```

### 2. 의존성 모킹

FastAPI의 Depends를 모킹합니다.

```python
def mock_get_review_service():
    return mock_review_service

monkeypatch.setattr(reviews, "get_review_service", lambda: mock_review_service)
```

### 3. 외부 리소스 모킹

파일, 네트워크 등 외부 리소스는 항상 모킹합니다.

```python
with patch("pathlib.Path.exists", return_value=True):
    with patch("builtins.open", mock_open(read_data="content")):
        result = function_that_reads_file()
```

## 테스트 네이밍 컨벤션

### 파일명
- `test_<모듈명>.py`
- 예: `test_review_service.py`, `test_resume_models.py`

### 클래스명
- `Test<테스트대상>`
- 예: `TestProfile`, `TestReviewService`

### 함수명
- `test_<무엇을>_<어떻게>` 형식
- 예: `test_profile_creation_success`
- 예: `test_review_introduction_with_invalid_data`

### Docstring
모든 테스트 함수에 간단한 docstring을 작성합니다.

```python
def test_profile_creation_success(self) -> None:
    """정상적인 Profile 생성."""
    ...
```

## 베스트 프랙티스

### 1. AAA 패턴 (Arrange-Act-Assert)
```python
def test_example(self) -> None:
    """테스트 예시."""
    # Arrange (준비)
    profile = Profile(...)

    # Act (실행)
    result = some_function(profile)

    # Assert (검증)
    assert result is not None
```

### 2. 각 테스트는 독립적
- 테스트 간 상태 공유 금지
- 순서에 의존하지 않기
- 필요시 `setup_method`로 초기화

### 3. 명확한 assertion
```python
# Good
assert response.status_code == 200
assert data["targetType"] == "introduction"

# Better (실패 시 메시지 포함)
assert response.status_code == 200, f"Unexpected status: {response.status_code}"
```

### 4. 외부 의존성은 항상 모킹
- AI API 호출
- 데이터베이스 접근
- 파일 시스템 접근
- 네트워크 요청

### 5. 테스트 데이터는 fixture로 관리
```python
@pytest.fixture
def sample_data() -> dict:
    """테스트용 데이터."""
    return {"key": "value"}
```

## CI/CD 통합

프로젝트의 pre-commit hook에 테스트가 포함되어 있습니다.

```bash
# pre-commit 실행
uv run pre-commit run --all-files

# 수동으로 테스트 + 린트 + 타입체크
uv run pytest
uv run ruff check backend tests
uv run mypy backend
```

## 트러블슈팅

### Import 오류
```bash
# PYTHONPATH 설정 확인
export PYTHONPATH="${PYTHONPATH}:${PWD}/backend"

# 또는 pytest 설정 확인
# pyproject.toml의 pythonpath = ["backend"] 설정 확인
```

### 비동기 테스트 오류
```python
# @pytest.mark.asyncio 데코레이터 추가
@pytest.mark.asyncio
async def test_async_function() -> None:
    result = await async_function()
    assert result is not None
```

### Mock이 제대로 동작하지 않을 때
```python
# monkeypatch 사용
def test_with_monkeypatch(monkeypatch) -> None:
    monkeypatch.setattr("module.function", mock_function)

# 또는 patch 사용
with patch("module.function", return_value=mock_value):
    result = function_that_uses_it()
```

## 참고 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [unittest.mock 문서](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
