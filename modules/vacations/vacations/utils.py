import logging
from datetime import date, datetime, time
from typing import Dict, Optional, List, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection  # noqa
from pymongo import ASCENDING

from fastapi_metabot.client import ApiClient, AsyncApis
from fastapi_metabot.client.models import SlackRequest
from fastapi_metabot.utils import (
    get_current_user_id,
    get_current_channel_id,
    command_metadata,
    action_metadata,
)
from vacations.config import (
    REQUEST_VIEW_ID,
    DATEPICKER_START_ACTION_ID,
    DATEPICKER_END_ACTION_ID,
    REASON_INPUT_ACTION_ID,
    APPROVE_BUTTON_ACTION_ID,
    DENY_BUTTON_ACTION_ID,
    ADMIN_CHANNEL
)

log = logging.getLogger(__name__)

APPROVAL_STATUSES = {
    'unapproved': ':eight_spoked_asterisk:',
    'approved': ':white_check_mark:',
    'denied': ':negative_squared_cross_mark:'
}

DIVIDER = {
    'type': 'divider'
}


async def send_ephemeral(
        metabot_client: ApiClient,
        text: str,
        blocks: Optional[List[Dict]] = None
) -> None:
    user = await get_current_user_id()
    log.info(f'Sending ephemeral to user {user}: {text}')
    api = AsyncApis(metabot_client).metabot_api
    await api.request_api_slack_post(
        SlackRequest(
            method='chat_postEphemeral',
            payload={
                'text': text,
                'blocks': blocks,
                'user': user,
                'channel': await get_current_channel_id()
            }
        )
    )


async def _send_notification(
        metabot_client: ApiClient,
        text: str,
        blocks: Optional[List[Dict]] = None,
        channel_id: Optional[str] = None,
        thread_ts: Optional[str] = None,
) -> None:
    if channel_id is None:
        channel_id = await get_current_user_id()

    log.info(f'Sending notification to channel {channel_id}: {text}')
    api = AsyncApis(metabot_client).metabot_api
    await api.request_api_slack_post(
        SlackRequest(
            method='chat_postMessage',
            payload={
                'text': text,
                'channel': channel_id,
                'blocks': blocks,
                'thread_ts': thread_ts
            }
        )
    )


async def _notify_admins(
        metabot_client: ApiClient,
        date_from: date,
        date_to: date,
        reason: str,
        request_id: str
) -> None:
    user = await get_current_user_id()
    blocks: List[Dict] = [
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
    await _send_notification(
        metabot_client,
        blocks[0]['text']['text'],
        blocks,
        ADMIN_CHANNEL
    )


async def create_request(
        metabot_client: ApiClient,
        collection: AsyncIOMotorCollection,
        date_from: date,
        date_to: Optional[date],
        reason: str,
) -> None:
    if date_to is None:
        date_to = date_from

    if date_from > date_to:
        date_to, date_from = date_from, date_to

    if date_from < date.today():
        return await send_ephemeral(
            metabot_client,
            'Start date of your leave must be today or in the future.'
        )

    request_id = str(
        await _save_request(
            collection,
            date_from,
            date_to,
            reason
        )
    )
    await _send_notification(
        metabot_client,
        f'Leave request #`{request_id}` has been created! '
        f'You will be notified when your request is approved or denied.'
    )
    await _notify_admins(
        metabot_client,
        date_from,
        date_to,
        reason,
        request_id
    )


def _build_request_view() -> Dict:
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


async def open_request_view(metabot_client: ApiClient) -> None:
    metadata = command_metadata.get()
    if metadata is None:
        raise ValueError('Must be called from command context')

    api = AsyncApis(metabot_client).metabot_api
    await api.request_api_slack_post(
        SlackRequest(
            method='views_open',
            payload={
                'trigger_id': metadata.trigger_id,
                'view': _build_request_view()
            }
        )
    )


async def _save_request(
        collection: AsyncIOMotorCollection,
        date_from: date,
        date_to: date,
        reason: str
) -> ObjectId:
    user = await get_current_user_id()
    datetime_from = datetime.combine(date_from, time.min)
    datetime_to = datetime.combine(date_to, time.min)
    result = await collection.insert_one({
        'user_id': user,
        'date_from': datetime_from,
        'date_to': datetime_to,
        'reason': reason,
        'approval_status': 'unapproved'
    })
    return result.inserted_id


async def parse_view() -> Tuple[date, date, str]:
    metadata = action_metadata.get()
    if not metadata or not metadata.view:
        raise ValueError('Must be called from view context')

    values = metadata.view['state']['values']
    date_from = date.fromisoformat(
        values['start'][DATEPICKER_START_ACTION_ID]['selected_date']
    )
    date_to = date.fromisoformat(
        values['end'][DATEPICKER_END_ACTION_ID]['selected_date']
    )
    reason = values['reason'][REASON_INPUT_ACTION_ID].get('value', '')
    return date_from, date_to, reason


async def process_request(
        collection: AsyncIOMotorCollection,
        metabot_client: ApiClient,
        request_id: str,
        status: str = 'approved'
) -> None:
    assert status in ('approved', 'denied')
    query = {'_id': ObjectId(request_id)}
    request = await collection.find_one(query)
    if request is None:
        return await send_ephemeral(
            metabot_client,
            f'Request #`{request_id}` does not exist.'
        )
    elif request['approval_status'] != 'unapproved':
        return await send_ephemeral(
            metabot_client,
            f'Request #`{request_id}` has already been processed.'
        )

    user = await get_current_user_id()
    await collection.update_one(query, {
        '$set': {'approval_status': status, 'admin_id': user}
    })
    await _send_notification(
        metabot_client,
        f'{APPROVAL_STATUSES[status]} '
        f'Your leave request #`{request_id}` has been {status} by <@{user}>.'
    )

    metadata = action_metadata.get()
    if metadata is not None and metadata.container is not None:
        thread_ts = metadata.container.get('message_ts')
    else:
        thread_ts = None
    await _send_notification(
        metabot_client,
        f'{APPROVAL_STATUSES[status]} '
        f'Request #`{request_id}` has been {status} by <@{user}>.',
        channel_id=ADMIN_CHANNEL,
        thread_ts=thread_ts
    )


async def get_request_id_from_button() -> str:
    metadata = action_metadata.get()
    if not metadata or not metadata.actions:
        raise ValueError('Must be called from action context')

    request_id = metadata.actions[0]['value']
    return request_id


async def is_admin_channel() -> bool:
    return await get_current_channel_id() == ADMIN_CHANNEL


async def send_history(
        collection: AsyncIOMotorCollection,
        metabot_client: ApiClient,
        user: Optional[str] = None
) -> None:
    current_user = await get_current_user_id()
    if user is None:
        user = current_user
    elif user != current_user and not await is_admin_channel():
        return await send_ephemeral(
            metabot_client,
            'This command is available only in the admin channel.'
        )

    blocks: List[Dict] = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'Leaves history for user <@{user}>:'
            }
        },
        DIVIDER
    ]
    cursor = collection.find({'user_id': user}).sort('date_from', ASCENDING)
    async for request in cursor:
        blocks += _build_history_blocks(request)
    await send_ephemeral(
        metabot_client,
        blocks[0]['text']['text'],
        blocks
    )


def _build_history_blocks(request: Dict) -> List[Dict]:
    date_from = request['date_from'].date()
    date_to = request['date_to'].date()
    reason = request["reason"]
    status = request['approval_status']
    emoji = APPROVAL_STATUSES.get(status, '')
    request_id = str(request['_id'])
    blocks = [
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
    return blocks
