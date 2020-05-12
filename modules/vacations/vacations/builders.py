from datetime import date
from typing import List, Dict

from vacations.config import (
    APPROVE_BUTTON_ACTION_ID,
    DENY_BUTTON_ACTION_ID,
    DATEPICKER_START_ACTION_ID,
    DATEPICKER_END_ACTION_ID,
    REASON_INPUT_ACTION_ID,
    REQUEST_VIEW_ID
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
        date_from: date,
        date_to: date,
        reason: str,
        request_id: str,
        user: str
) -> List[Dict]:
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'<!channel>\n<@{user}> has requested to go on a leave.'
            }
        },
        {
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f'*Start:*\n{date_from.isoformat()}'
                },
                {
                    'type': 'mrkdwn',
                    'text': f'*End:*\n{date_to.isoformat()}'
                }
            ]
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*Reason:*\n{reason}'
            }
        },
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


def build_request_view() -> Dict:
    today = date.today().isoformat()
    blocks = [
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


def build_history_blocks(history: List[Dict], user_id: str) -> List[Dict]:
    blocks: List[Dict] = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'Leaves history for user <@{user_id}>:'
            }
        },
        DIVIDER
    ]
    for request in history:
        blocks += _build_request_blocks(request)
    return blocks


def _build_request_blocks(request: Dict) -> List[Dict]:
    date_from = request['date_from'].date()
    date_to = request['date_to'].date()
    reason = request["reason"]
    status = request['approval_status']
    emoji = STATUS_EMOJIS.get(status, '')
    request_id = str(request['_id'])
    return [
        {
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
                    'text': f'*Reason:*\n{reason}'
                },
                {
                    'type': 'mrkdwn',
                    'text': f'*Status:*\n{emoji} {status.capitalize()}'
                },
            ]
        },
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
