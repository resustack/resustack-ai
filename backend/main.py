import sys

import uvicorn

from backend.api.rest.config import get_api_config

api_config = get_api_config()


def run_dev():
    """개발 서버 실행 (auto-reload 활성화)."""
    print("Running development server...")
    uvicorn.run(
        "backend.api.rest.main:app",
        host=api_config.app_host,
        port=api_config.app_port,
        reload=True,
    )


def run_prod():
    """프로덕션 서버 실행 (멀티 워커)."""
    print("Running production server...")
    uvicorn.run(
        "backend.api.rest.main:app",
        host=api_config.app_host,
        port=api_config.app_port,
        workers=4,
    )


if __name__ == "__main__":
    # CLI 인자로 실행 모드 결정
    mode = sys.argv[1] if len(sys.argv) > 1 else "auto"

    if mode == "dev":
        run_dev()
    elif mode == "prod":
        run_prod()
    else:
        if api_config.is_dev:
            run_dev()
        else:
            run_prod()
