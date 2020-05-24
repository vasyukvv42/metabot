from starlette.config import Config


config = Config('.env')

MODULE_URL = config('MODULE_URL')
METABOT_URL = config('METABOT_URL')
HEARTBEAT_DELAY = config('HEARTBEAT_DELAY', cast=float, default='10')

COMMANDS_BUTTON_ACTION_ID = config(
    'COMMANDS_BUTTON_ACTION_ID',
    default='help_commands_button'
)
