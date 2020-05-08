from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from metabot.lib.chat import send_message
from metabot.models.chat import Message

router = APIRouter()


class SendMessageResponse(BaseModel):
    ok: bool


@router.post('/', response_model=SendMessageResponse)
async def send_message_to_slack(
        message: Message,
        request: Request
) -> SendMessageResponse:
    await send_message(message, request.app.state.slack)
    return SendMessageResponse(ok=True)
