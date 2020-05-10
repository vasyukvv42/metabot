import logging

from fastapi import HTTPException
from slack import WebClient
from slack.errors import SlackApiError
from starlette.requests import Request

from metabot.models.chat import Message

log = logging.getLogger(__name__)


async def get_slack(request: Request) -> WebClient:
    return request.app.state.slack


async def send_message(
        slack: WebClient,
        message: Message,
) -> None:
    try:
        if message.send_ephemeral:
            await slack.chat_postEphemeral(
                channel=message.channel_id,
                user=message.user_id,
                text=message.text,
                blocks=message.blocks,
            )
        else:
            await slack.chat_postMessage(
                channel=message.channel_id,
                text=message.text,
                blocks=message.blocks,
            )
    except SlackApiError as e:
        log.exception('Failed to send message')
        raise HTTPException(e.response.status_code, e.response.get('error'))
