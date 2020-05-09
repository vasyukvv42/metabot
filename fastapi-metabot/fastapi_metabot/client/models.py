from typing import Any  # noqa
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Command(BaseModel):
    name: "str" = Field(..., alias="name")
    description: "Optional[str]" = Field(None, alias="description")
    arguments: "Optional[List[CommandArgument]]" = Field(None, alias="arguments")


class CommandArgument(BaseModel):
    name: "str" = Field(..., alias="name")
    is_optional: "Optional[bool]" = Field(None, alias="is_optional")
    description: "Optional[str]" = Field(None, alias="description")


class GetModulesResponse(BaseModel):
    modules: "Dict[str, Module]" = Field(..., alias="modules")


class HTTPValidationError(BaseModel):
    detail: "Optional[List[ValidationError]]" = Field(None, alias="detail")


class Message(BaseModel):
    channel_id: "str" = Field(..., alias="channel_id")
    text: "str" = Field(..., alias="text")
    blocks: "Optional[List[Any]]" = Field(None, alias="blocks")
    send_ephemeral: "Optional[bool]" = Field(None, alias="send_ephemeral")
    user_id: "Optional[str]" = Field(None, alias="user_id")


class Module(BaseModel):
    name: "str" = Field(..., alias="name")
    description: "Optional[str]" = Field(None, alias="description")
    url: "str" = Field(..., alias="url")
    commands: "Dict[str, Command]" = Field(..., alias="commands")


class SendMessageResponse(BaseModel):
    ok: "bool" = Field(..., alias="ok")


class ValidationError(BaseModel):
    loc: "List[str]" = Field(..., alias="loc")
    msg: "str" = Field(..., alias="msg")
    type: "str" = Field(..., alias="type")
