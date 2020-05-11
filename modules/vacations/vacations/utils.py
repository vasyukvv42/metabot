import logging

from fastapi_metabot.client import ApiClient, AsyncApis
from fastapi_metabot.client.models import SlackRequest
from fastapi_metabot.utils import get_current_user_id, get_current_channel_id

log = logging.getLogger(__name__)


async def send_error(
        metabot_client: ApiClient,
        text: str,
) -> None:
    api = AsyncApis(metabot_client).metabot_api
    resp = await api.request_api_slack_post(
        SlackRequest(
            method='chat_postEphemeral',
            payload={
                'text': text,
                'user': await get_current_user_id(),
                'channel': await get_current_channel_id()
            }
        )
    )
    log.debug(resp.data)
