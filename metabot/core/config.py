from starlette.config import Config

APP_TITLE = 'MetaBot'
API_PREFIX = '/api'
SLACKERS_PREFIX = '/slack'

config = Config('.env')

SLACK_SIGNING_SECRET = config('SLACK_SIGNING_SECRET')
SLACK_API_TOKEN = config('SLACK_API_TOKEN')
