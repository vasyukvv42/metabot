from starlette.config import Config

MAX_QUESTIONS = 95

config = Config('.env')

MODULE_URL = config('MODULE_URL')
METABOT_URL = config('METABOT_URL')
MONGODB_URI = config('MONGODB_URI')
FEEDBACK_COLLECTION = config('FEEDBACK_COLLECTION', default='feedback')
HEARTBEAT_DELAY = config('HEARTBEAT_DELAY', cast=float, default='10')

CREATION_VIEW_ID = config('CREATION_VIEW_ID', default='feedback_creation_view')
ANSWER_VIEW_ID = config('ANSWER_VIEW_ID', default='feedback_answer_view')
TITLE_INPUT_ACTION_ID = config(
    'TITLE_INPUT_ACTION_ID',
    default='feedback_title_input'
)
RECIPIENTS_SELECT_ACTION_ID = config(
    'RECIPIENTS_SELECT_ACTION_ID',
    default='feedback_recipients_select'
)
QUESTION_INPUT_ACTION_ID = config(
    'QUESTION_INPUT_ACTION_ID',
    default='feedback_question_input_{}'  # use .format()
)
ANSWER_INPUT_ACTION_ID = config(
    'ANSWER_INPUT_ACTION_ID',
    default='feedback_answer_input_{}'  # use .format()
)
NOTIFY_ACTION_ID = config(
    'NOTIFY_ACTION_ID',
    default='feedback_notify_button'
)
ANSWER_ACTION_ID = config(
    'ANSWER_ACTION_ID',
    default='feedback_answer_button'
)
