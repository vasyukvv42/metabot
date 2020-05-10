import logging
from typing import Dict, List, Iterable, Optional

from fastapi_metabot.client import ApiClient, AsyncApis
from fastapi_metabot.client.models import Module, Message
from fastapi_metabot.utils import slack_metadata

log = logging.getLogger(__name__)

DIVIDER = {
    'type': 'divider'
}


async def get_module(metabot_client: ApiClient, module_name: str) -> Module:
    api = AsyncApis(metabot_client).metabot_api
    module = (
        await api.get_module_by_name_api_modules_module_name_get(module_name)
    )
    return module


async def get_all_modules(metabot_client: ApiClient) -> Iterable[Module]:
    api = AsyncApis(metabot_client).metabot_api
    return (await api.get_modules_api_modules_get()).modules.values()


async def send_ephemeral_to_user(
        metabot_client: ApiClient,
        text: str,
        blocks: Optional[List[Dict]] = None
) -> None:
    api = AsyncApis(metabot_client).metabot_api
    metadata = slack_metadata.get()
    if metadata:
        await api.send_message_to_slack_api_chat_post(
            Message(
                text=text,
                blocks=blocks,
                user_id=metadata.user_id,
                channel_id=metadata.channel_id,
                send_ephemeral=True
            )
        )
    else:
        log.error('Failed sending message – no Slack metadata in ctx')


async def generate_default_help(metabot_client: ApiClient) -> List[Dict]:
    modules = await get_all_modules(metabot_client)
    blocks: List[Dict] = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*Usage:* `/meta help me "module_name"`. '
                        'Available modules:'
            }
        },
        DIVIDER
    ]
    for module in modules:
        blocks += _module_blocks(module)
    return blocks


async def generate_module_help(
        metabot_client: ApiClient,
        module_name: str,
) -> List[Dict]:
    module = await get_module(metabot_client, module_name)
    blocks: List[Dict] = _module_blocks(module)
    for command in module.commands.values():
        if command.arguments is not None:
            arguments_short = ' '.join(
                f'"{arg.name}"' for arg in command.arguments
            )
            arguments_long = '\n'.join(
                f'- *{arg.name}* '
                f'{arg.description if arg.description else ""} '
                f'{"_(optional)_" if arg.is_optional else ""}'
                for arg in command.arguments
            )
        else:
            arguments_short = ''
            arguments_long = ''

        full_command = f'`/meta {module_name} {command.name} {arguments_short}`'
        blocks += [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'{full_command}\n'
                            f'{command.description}\n'
                            f'{arguments_long}'
                }
            },
            DIVIDER
        ]
    return blocks


def _module_blocks(module: Module) -> List[Dict]:
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*`{module.name}` module.*\n{module.description}'
            }
        },
        DIVIDER
    ]
