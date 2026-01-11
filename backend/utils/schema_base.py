from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        # Python 내부(snake_case) -> 외부(camelCase) 변환
        alias_generator=to_camel,
        # 외부에서 보내준 camelCase 데이터를 내부 snake_case 변수에 매핑
        populate_by_name=True,
        # 응답 시 alias(camelCase)를 사용하도록 설정
        serialize_by_alias=True
    )
