# flake8: noqa
from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING

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


async def get_current_user_id() -> Optional[str]:
    if c := command_metadata.get():
        return c.user_id
    elif a := action_metadata.get():
        user = a.user or {}
        return user.get('id')
    return None


async def get_current_channel_id() -> Optional[str]:
    if c := command_metadata.get():
        return c.channel_id
    elif a := action_metadata.get():
        channel = a.channel or {}
        return channel.get('id')
    return None
