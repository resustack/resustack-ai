from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

# Camel case 변환을 위한 공통 ConfigDict
CAMEL_CONFIG = ConfigDict(
    # Python 내부(snake_case) -> 외부(camelCase) 변환
    alias_generator=to_camel,
    # 외부에서 보내준 camelCase 데이터를 내부 snake_case 변수에 매핑
    populate_by_name=True,
    # 응답 시 alias(camelCase)를 사용하도록 설정
    serialize_by_alias=True,
)


class CamelModel(BaseModel):
    """Camel case 변환이 적용된 기본 모델."""

    model_config = CAMEL_CONFIG


class CamelCaseMixin:
    """Camel case 변환 Mixin.

    다른 모델을 상속받으면서 camelCase 변환이 필요할 때 사용합니다.

    Example:
        class MyRequest(CamelCaseMixin, SomeBaseModel):
            pass
    """

    model_config = CAMEL_CONFIG
