from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING, Dict

from fastapi_metabot.client import SyncApis, AsyncApis
from fastapi_metabot.client.models import SlackRequest

if TYPE_CHECKING:
    from fastapi_metabot.models import CommandMetadata, ActionMetadata  # noqa
    from fastapi_metabot.module import Module  # noqa


command_metadata: ContextVar[Optional['CommandMetadata']] = ContextVar(
    'command_metadata',
    default=None
)

action_metadata: ContextVar[Optional['ActionMetadata']] = ContextVar(
    'action_metadata',
    default=None
)

current_module: ContextVar[Optional['Module']] = ContextVar(
    'current_module',
    default=None
)


def get_current_user_id() -> Optional[str]:
    if c := command_metadata.get():
        return c.user_id
    elif a := action_metadata.get():
        user = a.user or {}
        return user.get('id')
    return None


def get_current_channel_id() -> Optional[str]:
    if c := command_metadata.get():
        return c.channel_id
    elif a := action_metadata.get():
        channel = a.channel or {}
        return channel.get('id')
    return None


def slack_request(method: str, payload: Dict) -> Dict:
    module = current_module.get()
    assert module is not None, 'Must be called from any Slack context'

    api = SyncApis(module.metabot_client).metabot_api
    resp = api.request_api_slack_post(
        SlackRequest(
            method=method,
            payload=payload
        )
    )
    return resp.data


async def async_slack_request(method: str, payload: Dict) -> Dict:
    module = current_module.get()
    assert module is not None, 'Must be called from any Slack context'

    api = AsyncApis(module.metabot_client).metabot_api
    resp = await api.request_api_slack_post(
        SlackRequest(
            method=method,
            payload=payload
        )
    )
    return resp.data
