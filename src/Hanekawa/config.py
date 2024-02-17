import re
from typing import Annotated, List, Optional

import tomllib
from pydantic import BaseModel, Field, ValidationInfo, field_validator

__all__ = ["Config", "load_config"]

ID_REGEX = re.compile(r"([0-9]{15,21})$")


class Config(BaseModel):
    token: Annotated[str, Field(min_length=1)]
    owners: List[int]
    database_url: str
    dev_guild: Optional[int] = None

    @field_validator("owners", "dev_guild")
    @classmethod
    def check_id_regex(cls, v: List[int] | int, info: ValidationInfo) -> List[int] | int:
        if isinstance(v, list):
            for id in v:
                if not ID_REGEX.match(str(id)):
                    raise ValueError(f"{info.field_name} - {id} isn't a valid Discord ID")
        else:
            if not ID_REGEX.match(str(v)):
                raise ValueError(f"{info.field_name} - {v} isn't a valid Discord ID")

        return v


def load_config(file: str) -> Config:
    with open(f"config/{file}", "r") as fp:
        config = tomllib.loads(fp.read())

    return Config(**config)
