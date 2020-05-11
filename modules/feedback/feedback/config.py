from starlette.config import Config

MAX_QUESTIONS = 95

config = Config('.env')

MODULE_URL = config('MODULE_URL')
METABOT_URL = config('METABOT_URL')
ADMIN_CHANNEL = config('ADMIN_CHANNEL')
MONGODB_URI = config('MONGODB_URI')
FEEDBACK_COLLECTION = config('FEEDBACK_COLLECTION', default='feedback')
