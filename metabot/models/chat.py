from typing import Optional, List, Dict, Any

from pydantic import BaseModel, validator


class Message(BaseModel):
    channel_id: str
    text: str
    blocks: Optional[List[Dict[str, Any]]]
    send_ephemeral: bool = False
    user_id: Optional[str]

    @validator('user_id', always=True)
    def user_id_provided_for_ephemeral(
            cls,  # noqa
            v: Optional[str],
            values: Dict[str, Any]
    ) -> Optional[str]:
        if values.get('send_ephemeral') and v is None:
            raise ValueError('user_id is required for ephemeral messages')
        return v
