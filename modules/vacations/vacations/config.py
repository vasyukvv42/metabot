from starlette.config import Config

config = Config('.env')

MODULE_URL = config('MODULE_URL')
METABOT_URL = config('METABOT_URL')
ADMIN_CHANNEL = config('ADMIN_CHANNEL')
MONGODB_URI = config('MONGODB_URI')
