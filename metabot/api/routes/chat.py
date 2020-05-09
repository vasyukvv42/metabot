from fastapi import APIRouter, Depends
from pydantic import BaseModel
from slack import WebClient

from metabot.lib.slack import send_message, get_slack
from metabot.models.chat import Message

router = APIRouter()


class SendMessageResponse(BaseModel):
    ok: bool


@router.post('/', response_model=SendMessageResponse)
async def send_message_to_slack(
        message: Message,
        slack: WebClient = Depends(get_slack),
) -> SendMessageResponse:
    await send_message(slack, message)
    return SendMessageResponse(ok=True)
