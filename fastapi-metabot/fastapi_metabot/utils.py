from contextvars import ContextVar
from typing import Optional

from fastapi_metabot.models import SlackMetadata
from fastapi_metabot.module import Module


slack_metadata: ContextVar[Optional[SlackMetadata]] = ContextVar(
    'slack_metadata',
    default=None
)

current_module: ContextVar[Optional[Module]] = ContextVar(
    'current_module',
    default=None
)
