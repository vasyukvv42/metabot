from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from slack import WebClient

from metabot.lib.slack import slack_request, get_slack
from metabot.models.slack import SlackRequest

router = APIRouter()


class SlackResponse(BaseModel):
    data: Dict


@router.post('/', response_model=SlackResponse)
async def request(
        req: SlackRequest,
        slack: WebClient = Depends(get_slack),
) -> SlackResponse:
    response = await slack_request(slack, req)
    return SlackResponse(data=response.data)
