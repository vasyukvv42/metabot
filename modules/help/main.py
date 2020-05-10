import logging

from fastapi import FastAPI

from config import MODULE_URL, METABOT_URL, MODULE_HELP_ACTION
from fastapi_metabot.module import Module
from utils import (
    generate_default_help,
    generate_module_help,
    send_ephemeral_to_user, get_module_name_from_button
)

log = logging.getLogger(__name__)
app = FastAPI()

module = Module(
    name='help',
    description='Provides info about MetaBot modules and their commands',
    module_url=MODULE_URL,
    metabot_url=METABOT_URL,
)


@module.command(
    'me',
    description='Displays help about a module',
    arg_descriptions={
        'module_name': 'Module name',
    }
)
async def get_help(module_name: str = None) -> None:
    if module_name is None:
        blocks = await generate_default_help(module.metabot_client)
    else:
        try:
            blocks = await generate_module_help(
                module.metabot_client,
                module_name
            )
        except Exception:  # noqa
            log.exception('Help generation failed, sending default help')
            return await get_help()

    await send_ephemeral_to_user(
        module.metabot_client,
        blocks[0]['text']['text'],
        blocks
    )


@module.action(MODULE_HELP_ACTION)
async def module_help_action() -> None:
    module_name = await get_module_name_from_button()
    blocks = await generate_module_help(
        module.metabot_client,
        module_name,
        False
    )
    await send_ephemeral_to_user(
        module.metabot_client,
        blocks[0]['text']['text'],
        blocks
    )

module.install(app)
