from typing import Dict

from pydantic import BaseModel


class SlackMetadata(BaseModel):
    token: str
    command: str
    response_url: str
    trigger_id: str
    user_id: str
    user_name: str
    channel_id: str
    text: str


class MetabotPayload(BaseModel):
    arguments: Dict[str, str]
    metadata: SlackMetadata
