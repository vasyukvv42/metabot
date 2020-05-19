from datetime import date
from decimal import Decimal
from typing import List, Dict, Iterable, Optional

from vacations.config import (
    APPROVE_BUTTON_ACTION_ID,
    DENY_BUTTON_ACTION_ID,
    DATEPICKER_START_ACTION_ID,
    DATEPICKER_END_ACTION_ID,
    REASON_INPUT_ACTION_ID,
    REQUEST_VIEW_ID,
    LEAVE_TYPES,
    VACATION_TYPE_ACTION_ID
)

STATUS_EMOJIS = {
    'unapproved': ':eight_spoked_asterisk:',
    'approved': ':white_check_mark:',
    'denied': ':negative_squared_cross_mark:'
}

DIVIDER = {
    'type': 'divider'
}


def build_admin_request_notification(
        leave_type: str,
        date_from: date,
        date_to: date,
        duration: int,
        days_left: int,
        reason: str,
        request_id: str,
        user: str
) -> List[Dict]:
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'<!channel>\n<@{user}> has requested to go on a leave '
                        f'for *{duration} days*.'
            }
        },
        _build_request_info_block(
            date_from, date_to, leave_type, reason, days_left
        ),
        {
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f'Request #`{request_id}`'
                }
            ]
        },
        {
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': {
                        'type': 'plain_text',
                        'emoji': True,
                        'text': 'Approve'
                    },
                    'style': 'primary',
                    'value': request_id,
                    'action_id': APPROVE_BUTTON_ACTION_ID
                },
                {
                    'type': 'button',
                    'text': {
                        'type': 'plain_text',
                        'emoji': True,
                        'text': 'Deny'
                    },
                    'style': 'danger',
                    'value': request_id,
                    'action_id': DENY_BUTTON_ACTION_ID
                }
            ]
        }
    ]


def build_request_view(days: Dict[str, Decimal]) -> Dict:
    today = date.today().isoformat()
    blocks = build_days_blocks(days) + [
        {
            'type': 'input',
            'block_id': 'type',
            'element': {
                'type': 'static_select',
                'action_id': VACATION_TYPE_ACTION_ID,
                'placeholder': {
                    'type': 'plain_text',
                    'text': 'Select an item',
                    'emoji': True
                },
                'options': [
                    {
                        'text': {
                            'type': 'plain_text',
                            'text': type_.capitalize(),
                            'emoji': True
                        },
                        'value': type_
                    } for type_ in LEAVE_TYPES
                ]
            },
            'label': {
                'type': 'plain_text',
                'text': 'Leave Type',
                'emoji': True
            }
        },
        {
            'type': 'input',
            'block_id': 'start',
            'element': {
                'type': 'datepicker',
                'action_id': DATEPICKER_START_ACTION_ID,
                'initial_date': today,
                'placeholder': {
                    'type': 'plain_text',
                    'text': 'Select a date',
                    'emoji': True
                }
            },
            'label': {
                'type': 'plain_text',
                'text': 'Start Date',
                'emoji': True
            },
            'hint': {
                'type': 'plain_text',
                'text': 'Pick a date you want to start your leave on'
            }
        },
        {
            'type': 'input',
            'block_id': 'end',
            'element': {
                'type': 'datepicker',
                'action_id': DATEPICKER_END_ACTION_ID,
                'initial_date': today,
                'placeholder': {
                    'type': 'plain_text',
                    'text': 'Select a date',
                    'emoji': True
                }
            },
            'label': {
                'type': 'plain_text',
                'text': 'End Date',
                'emoji': True
            },
            'hint': {
                'type': 'plain_text',
                'text': 'Pick a date you want to end your leave on'
            }
        },
        {
            'type': 'input',
            'block_id': 'reason',
            'optional': True,
            'element': {
                'type': 'plain_text_input',
                'action_id': REASON_INPUT_ACTION_ID,
                'multiline': True
            },
            'label': {
                'type': 'plain_text',
                'text': 'Reason'
            },
            'hint': {
                'type': 'plain_text',
                'text': 'The reason for your leave'
            }
        }
    ]
    return {
        'type': 'modal',
        'callback_id': REQUEST_VIEW_ID,
        'title': {
            'type': 'plain_text',
            'text': 'Request a leave',
            'emoji': True
        },
        'submit': {
            'type': 'plain_text',
            'text': 'Request',
            'emoji': True
        },
        'close': {
            'type': 'plain_text',
            'text': 'Cancel',
            'emoji': True
        },
        'blocks': blocks
    }


def build_history_blocks(history: Iterable[Dict]) -> List[Dict]:
    blocks: List[Dict] = [DIVIDER]
    for request in history:
        blocks += _build_request_blocks(request)
    return blocks


def _build_request_blocks(request: Dict) -> List[Dict]:
    date_from = request['date_from'].date()
    date_to = request['date_to'].date()
    leave_type = request['leave_type']
    reason = request['reason']
    request_id = str(request['_id'])
    return [
        _build_request_info_block(date_from, date_to, leave_type, reason),
        {
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f'Request #`{request_id}`'
                }
            ]
        },
        DIVIDER
    ]


def _build_request_info_block(
        date_from: date,
        date_to: date,
        leave_type: str,
        reason: str,
        days_left: Optional[int] = None,
) -> Dict:
    days_left_text = (
        f'(*{days_left} days* left)' if days_left is not None else ''
    )
    return {
        'type': 'section',
        'fields': [
            {
                'type': 'mrkdwn',
                'text': f'*Start:*\n{date_from.isoformat()}'
            },
            {
                'type': 'mrkdwn',
                'text': f'*End:*\n{date_to.isoformat()}'
            },
            {
                'type': 'mrkdwn',
                'text': f'*Type:*\n{leave_type.capitalize()} {days_left_text}'
            },
            {
                'type': 'mrkdwn',
                'text': f'*Reason:*\n{reason}'
            },
        ]
    }


def build_days_blocks(days: Dict[str, Decimal]) -> List[Dict]:
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': 'Days available:'
            }
        },
        {
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f'*{type_.capitalize()}:* {int(value)}'
                } for type_, value in days.items()
            ]
        }
    ]
