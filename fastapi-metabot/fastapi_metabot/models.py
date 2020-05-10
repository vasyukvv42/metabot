from typing import Dict, List, Optional

from pydantic import BaseModel


class CommandMetadata(BaseModel):
    token: str
    command: str
    response_url: str
    trigger_id: str
    user_id: str
    user_name: str
    channel_id: str
    text: str


class CommandPayload(BaseModel):
    arguments: Dict[str, str]
    metadata: CommandMetadata


class ActionMetadata(BaseModel):
    type: str  # noqa
    token: Optional[str]
    team: Optional[Dict]
    user: Optional[Dict]
    response_url: Optional[str]
    actions: Optional[List[Dict]]
    api_app_id: Optional[str]
    callback_id: Optional[str]
    channel: Optional[Dict]
    container: Optional[Dict]
    hash: Optional[str]  # noqa
    is_cleared: Optional[bool]
    message: Optional[Dict]
    trigger_id: Optional[str]
    view: Optional[Dict]


class ActionPayload(BaseModel):
    metadata: ActionMetadata
