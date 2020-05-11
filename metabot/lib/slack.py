import logging

from fastapi import HTTPException
from slack import WebClient
from slack.errors import SlackApiError
from slack.web.slack_response import SlackResponse
from starlette.requests import Request

from metabot.models.slack import SlackRequest

log = logging.getLogger(__name__)


async def get_slack(request: Request) -> WebClient:
    return request.app.state.slack


async def slack_request(slack: WebClient, req: SlackRequest) -> SlackResponse:
    try:
        method = getattr(slack, req.method.value)
        return await method(**req.payload)
    except SlackApiError as e:
        log.exception('Slack request failed')
        raise HTTPException(e.response.status_code, e.response.get('error'))
