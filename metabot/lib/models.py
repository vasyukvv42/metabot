from typing import List, Optional, Dict

from pydantic import BaseModel, AnyHttpUrl


class CommandArgument(BaseModel):
    name: str
    optional: bool = False
    description: Optional[str]


class Command(BaseModel):
    name: str
    description: Optional[str]
    arguments: List[CommandArgument]


class Module(BaseModel):
    name: str
    description: Optional[str]
    url: AnyHttpUrl

    commands: Dict[str, Command]
