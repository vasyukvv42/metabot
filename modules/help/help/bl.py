import logging
from typing import Dict, List, Iterable, Optional

from help.builders import build_default_help, build_module_help
from fastapi_metabot.client import ApiClient, AsyncApis
from fastapi_metabot.client.models import Module, SlackRequest
from fastapi_metabot.utils import (
    get_current_user_id,
    get_current_channel_id,
    action_metadata
)

log = logging.getLogger(__name__)


async def send_help(
        metabot_client: ApiClient,
        module_name: Optional[str] = None
) -> None:
    if module_name is None:
        return await _send_default_help(metabot_client)

    try:
        module = await _get_module(metabot_client, module_name)
        blocks = build_module_help(module)
    except Exception:  # noqa
        log.exception('Help generation failed, sending default help')
        return await send_help(metabot_client)

    await _send_message_to_user(
        metabot_client,
        blocks[0]['text']['text'],
        blocks
    )


async def _send_default_help(metabot_client: ApiClient) -> None:
    modules = await _get_all_modules(metabot_client)
    blocks = build_default_help(modules)
    await _send_message_to_user(
        metabot_client,
        blocks[0]['text']['text'],
        blocks
    )


async def get_module_name_from_button() -> str:
    metadata = action_metadata.get()
    assert metadata and metadata.actions, 'Must be called from action context'

    action = metadata.actions[0]
    return action['value']


async def _get_module(metabot_client: ApiClient, module_name: str) -> Module:
    api = AsyncApis(metabot_client).metabot_api
    module = (
        await api.get_module_by_name_api_modules_module_name_get(module_name)
    )
    return module


async def _get_all_modules(metabot_client: ApiClient) -> Iterable[Module]:
    api = AsyncApis(metabot_client).metabot_api
    return (await api.get_modules_api_modules_get()).modules.values()


async def _send_message_to_user(
        metabot_client: ApiClient,
        text: str,
        blocks: Optional[List[Dict]] = None
) -> None:
    api = AsyncApis(metabot_client).metabot_api
    await api.request_api_slack_post(
        SlackRequest(
            method='chat_postEphemeral',
            payload={
                'text': text,
                'blocks': blocks,
                'user': await get_current_user_id(),
                'channel': await get_current_channel_id()
            }
        )
    )
