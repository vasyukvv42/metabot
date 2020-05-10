from fastapi import APIRouter, Depends
from pydantic import BaseModel
from slack import WebClient

from metabot.lib.slack import post_message, get_slack
from metabot.models.chat import Message

router = APIRouter()


class SendMessageResponse(BaseModel):
    ok: bool


@router.post('/', response_model=SendMessageResponse)
async def send_message(
        message: Message,
        slack: WebClient = Depends(get_slack),
) -> SendMessageResponse:
    await post_message(slack, message)
    return SendMessageResponse(ok=True)
