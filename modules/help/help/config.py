from starlette.config import Config

MODULE_HELP_ACTION = 'module_help_action'

config = Config('.env')

MODULE_URL = config('MODULE_URL')
METABOT_URL = config('METABOT_URL')
