from typing import List, Dict, Iterable

from fastapi_metabot.client.models import Module
from help.config import COMMANDS_BUTTON_ACTION_ID

DIVIDER = {
    'type': 'divider'
}


def build_default_help(modules: Iterable[Module]) -> List[Dict]:
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
        blocks += build_module_blocks(module, True)
    return blocks


def build_module_help(module: Module) -> List[Dict]:
    blocks: List[Dict] = build_module_blocks(module)

    for command in module.commands.values():
        if command.arguments is not None:
            arguments_short = ' '.join(
                f'"{arg.name}"' for arg in command.arguments
            )
            arguments_long = '\n'.join(
                f'• *{arg.name}*\t'
                f'{arg.description if arg.description else ""} '
                f'{"_(optional)_" if arg.is_optional else ""}'
                for arg in command.arguments
            )
        else:
            arguments_short = ''
            arguments_long = ''

        full_command = f'`/meta {module.name} {command.name} {arguments_short}`'
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


def build_module_blocks(module: Module, add_button: bool = False) -> List[Dict]:
    module_section = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': f'*`{module.name}` module*\n{module.description}'
        }
    }
    if add_button:
        module_section['accessory'] = {
            'action_id': COMMANDS_BUTTON_ACTION_ID,
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
