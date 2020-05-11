import logging
from typing import Dict, List, Iterable, Optional

from help.config import MODULE_HELP_ACTION
from fastapi_metabot.client import ApiClient, AsyncApis
from fastapi_metabot.client.models import Module, SlackRequest
from fastapi_metabot.utils import (
    get_current_user_id,
    get_current_channel_id,
    action_metadata
)

log = logging.getLogger(__name__)

DIVIDER = {
    'type': 'divider'
}


async def get_module_name_from_button() -> str:
    metadata = action_metadata.get()
    if metadata is None or metadata.actions is None:
        raise ValueError('Must be called from action context')
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


async def send_message_to_user(
        metabot_client: ApiClient,
        text: str,
        blocks: Optional[List[Dict]] = None
) -> None:
    api = AsyncApis(metabot_client).metabot_api
    resp = await api.request_api_slack_post(
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
    log.debug(resp.data)


async def generate_default_help(metabot_client: ApiClient) -> List[Dict]:
    modules = await _get_all_modules(metabot_client)
    blocks: List[Dict] = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*Available modules:*'
            }
        },
        DIVIDER
    ]
    for module in modules:
        blocks += _module_blocks(module, True)
    return blocks


async def generate_module_help(
        metabot_client: ApiClient,
        module_name: str,
        include_module_description: bool = True,
) -> List[Dict]:
    module = await _get_module(metabot_client, module_name)
    blocks: List[Dict] = []
    if include_module_description:
        blocks += _module_blocks(module)

    for command in module.commands.values():
        if command.arguments is not None:
            arguments_short = ' '.join(
                f'"{arg.name}"' for arg in command.arguments
            )
            arguments_long = '\n'.join(
                f'- *{arg.name}*\t'
                f'{arg.description if arg.description else ""} '
                f'{"_(optional)_" if arg.is_optional else ""}'
                for arg in command.arguments
            )
        else:
            arguments_short = ''
            arguments_long = ''

        full_command = f'`/meta {module_name} {command.name} {arguments_short}`'
        description = command.description or ''
        blocks += [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'{full_command}\n'
                            f'{description}\n\n'
                            f'{arguments_long}'
                }
            },
            DIVIDER
        ]
    return blocks


def _module_blocks(module: Module, add_button: bool = False) -> List[Dict]:
    module_section = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': f'*`{module.name}` module*\n{module.description}'
        }
    }
    if add_button:
        module_section['accessory'] = {
            'action_id': MODULE_HELP_ACTION,
            'type': 'button',
            'text': {
                'type': 'plain_text',
                'emoji': True,
                'text': 'Commands'
            },
            'value': module.name
        }
    return [
        module_section,
        DIVIDER
    ]
