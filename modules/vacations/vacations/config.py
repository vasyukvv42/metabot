from starlette.config import Config

config = Config('.env')

MODULE_URL = config('MODULE_URL')
METABOT_URL = config('METABOT_URL')
ADMIN_CHANNEL = config('ADMIN_CHANNEL')
MONGODB_URI = config('MONGODB_URI')
HISTORY_COLLECTION = config('HISTORY_COLLECTION', default='history')

REQUEST_VIEW_ID = config('REQUEST_VIEW_ID', default='vacations_request_view')
APPROVE_BUTTON_ACTION_ID = config(
    'APPROVE_BUTTON_ACTION_ID',
    default='vacations_approve_button'
)
DENY_BUTTON_ACTION_ID = config(
    'DENY_BUTTON_ACTION_ID',
    default='vacations_deny_button'
)

DATEPICKER_START_ACTION_ID = config(
    'DATEPICKER_START_ACTION_ID',
    default='vacations_start_datepicker'
)
DATEPICKER_END_ACTION_ID = config(
    'DATEPICKER_END_ACTION_ID',
    default='vacations_end_datepicker'
)
REASON_INPUT_ACTION_ID = config(
    'REASON_INPUT_ACTION_ID',
    default='vacations_reason_input'
)
