from typing import Dict

from bson import Decimal128
from starlette.config import Config

config = Config('.env')

MODULE_URL = config('MODULE_URL')
METABOT_URL = config('METABOT_URL')
ADMIN_CHANNEL = config('ADMIN_CHANNEL')
ANNOUNCE_CHANNEL = config('ANNOUNCE_CHANNEL')
MONGODB_URI = config('MONGODB_URI')
HISTORY_COLLECTION = config('HISTORY_COLLECTION', default='history')
USERS_COLLECTION = config('USERS_COLLECTION', default='users')


def _cast_vacation_types(vacation_types: str) -> Dict[str, Decimal128]:
    result = {}
    for type_ in vacation_types.split(';'):
        key, value = type_.split(':') if ':' in type_ else (type_, '0')
        result[key] = Decimal128(value)
    return result


VACATION_TYPES = config(
    'VACATION_TYPES',  # type : days added per week (separated by semicolon)
    cast=_cast_vacation_types,
    default='vacation:0.47;day off:0.06;sick'
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
