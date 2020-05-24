import logging

from fastapi import FastAPI

from help.config import (
    MODULE_URL,
    METABOT_URL,
    COMMANDS_BUTTON_ACTION_ID,
    HEARTBEAT_DELAY
)
from fastapi_metabot.module import Module
from help.bl import get_module_name_from_button, send_help

log = logging.getLogger(__name__)
app = FastAPI()

module = Module(
    name='help',
    description=':sos: Get info about installed MetaBot modules and commands',
    module_url=MODULE_URL,
    metabot_url=METABOT_URL,
    heartbeat_delay=HEARTBEAT_DELAY,
)


@module.command(
    'me',
    description='Displays info about a module and lists available commands.\n'
                'When module name is not provided, displays short info about '
                'all modules.',
    arg_descriptions={
        'module_name': 'Module name',
    }
)
async def get_help(module_name: str = None) -> None:
    await send_help(module.metabot_client, module_name)


@module.action(COMMANDS_BUTTON_ACTION_ID)
async def module_help_action() -> None:
    module_name = await get_module_name_from_button()
    await send_help(module.metabot_client, module_name)


module.install(app)
