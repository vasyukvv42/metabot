from starlette.config import Config

APP_TITLE = 'MetaBot'
API_PREFIX = '/api'
SLACKERS_PREFIX = '/slack'

config = Config('.env')

SLACK_SIGNING_SECRET = config('SLACK_SIGNING_SECRET')
SLACK_API_TOKEN = config('SLACK_API_TOKEN')
REDIS_URL = config('REDIS_URL')
MODULE_EXPIRATION_SECONDS = config(
    'MODULE_EXPIRATION_SECONDS',
    cast=int,
    default=30,
)
