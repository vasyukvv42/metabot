from typing import Dict

from bson import Decimal128
from starlette.config import Config

config = Config('.env')

MODULE_URL = config('MODULE_URL')
METABOT_URL = config('METABOT_URL')
ADMIN_CHANNEL = config('ADMIN_CHANNEL')
MONGODB_URI = config('MONGODB_URI')
ANNOUNCE_CHANNEL = config('ANNOUNCE_CHANNEL', default='#announcements')
HISTORY_COLLECTION = config('HISTORY_COLLECTION', default='history')
USERS_COLLECTION = config('USERS_COLLECTION', default='users')
HEARTBEAT_DELAY = config('HEARTBEAT_DELAY', cast=float, default='10')


def _cast_leave_types(vacation_types: str) -> Dict[str, Decimal128]:
    result = {}
    for type_ in vacation_types.split(';'):
        key, value = type_.split(':') if ':' in type_ else (type_, '0')
        result[key] = Decimal128(value)
    return result


LEAVE_TYPES = config(
    'LEAVE_TYPES',  # type : days added per cronjob (separated by semicolon)
    cast=_cast_leave_types,
    default='vacation:0.1;sick:0.08;day-off:0.02'
)

REQUEST_VIEW_ID = config('REQUEST_VIEW_ID', default='vacations_request_view')
APPROVE_BUTTON_ACTION_ID = config(
    'APPROVE_BUTTON_ACTION_ID',
    default='vacations_approve_button'
)
DENY_BUTTON_ACTION_ID = config(
    'DENY_BUTTON_ACTION_ID',
    default='vacations_deny_button'
)

VACATION_TYPE_ACTION_ID = config(
    'VACATION_TYPE_ACTION_ID',
    default='vacations_type_select'
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
