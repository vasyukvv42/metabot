import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Optional, List, Tuple

from motor.motor_asyncio import AsyncIOMotorCollection  # noqa

from fastapi_metabot.utils import (
    get_current_user_id,
    get_current_channel_id,
    command_metadata,
    action_metadata,
    async_slack_request,
)
from vacations.builders import (
    build_admin_request_notification,
    build_request_view,
    build_history_blocks,
    STATUS_EMOJIS, build_days_blocks
)
from vacations.config import (
    DATEPICKER_START_ACTION_ID,
    DATEPICKER_END_ACTION_ID,
    REASON_INPUT_ACTION_ID,
    ADMIN_CHANNEL,
    LEAVE_TYPES,
    VACATION_TYPE_ACTION_ID
)
from vacations.db import (
    save_request,
    update_request_status,
    get_request_by_id,
    get_leaves_history_by_user_id,
    get_days_by_user_id,
    increase_days_by_user,
    increase_days
)

log = logging.getLogger(__name__)


async def send_ephemeral(
        text: str,
        blocks: Optional[List[Dict]] = None
) -> None:
    user = get_current_user_id()
    log.info(f'Sending ephemeral to user {user}: {text}')
    await async_slack_request(
        method='chat_postEphemeral',
        payload={
            'text': text,
            'blocks': blocks,
            'user': user,
            'channel': get_current_channel_id()
        }
    )


async def _send_notification(
        text: str,
        blocks: Optional[List[Dict]] = None,
        channel_id: Optional[str] = None,
        thread_ts: Optional[str] = None,
) -> None:
    if channel_id is None:
        channel_id = get_current_user_id()

    log.info(f'Sending notification to channel {channel_id}: {text}')
    await async_slack_request(
        method='chat_postMessage',
        payload={
            'text': text,
            'channel': channel_id,
            'blocks': blocks,
            'thread_ts': thread_ts
        }
    )


async def _notify_admins(
        leave_type: str,
        date_from: date,
        date_to: date,
        duration: int,
        days_left: int,
        reason: str,
        request_id: str
) -> None:
    user = get_current_user_id()
    assert user is not None, 'Must be called from any Slack context'

    blocks = build_admin_request_notification(
        leave_type,
        date_from,
        date_to,
        duration,
        days_left,
        reason,
        request_id,
        user
    )
    await _send_notification(
        blocks[0]['text']['text'],
        blocks,
        ADMIN_CHANNEL
    )


async def create_request(
        history: AsyncIOMotorCollection,
        users: AsyncIOMotorCollection,
        leave_type: str,
        date_from: Optional[date],
        date_to: Optional[date],
        reason: str,
) -> None:
    user = get_current_user_id()
    assert user is not None, 'Must be called from any Slack context'

    if leave_type not in LEAVE_TYPES:
        return await send_ephemeral(
            f'Leave type must be one of `{"` `".join(LEAVE_TYPES)}`'
        )

    if date_from is None:
        date_from = date.today()

    if date_to is None:
        date_to = date_from

    if date_from > date_to:
        date_to, date_from = date_from, date_to

    if date_from < date.today():
        return await send_ephemeral(
            'Start date of your leave must be today or in the future.'
        )

    duration = (date_to - date_from).days + 1
    days = await get_days_by_user_id(users, user)
    request_id = await save_request(
        history,
        leave_type,
        date_from,
        date_to,
        duration,
        reason,
        user,
    )
    await _send_notification(
        f'Leave request #`{request_id}` has been created! '
        f'You will be notified when your request is approved or denied.'
    )
    await _notify_admins(
        leave_type,
        date_from,
        date_to,
        duration,
        int(days[leave_type]),
        reason,
        request_id
    )


async def open_request_view(users: AsyncIOMotorCollection) -> None:
    metadata = command_metadata.get()
    user = get_current_user_id()
    assert metadata and user, 'Must be called from command context'

    days = await get_days_by_user_id(users, user)
    await async_slack_request(
        method='views_open',
        payload={
            'trigger_id': metadata.trigger_id,
            'view': build_request_view(days)
        }
    )


def parse_request_view() -> Tuple[str, date, date, str]:
    metadata = action_metadata.get()
    assert metadata and metadata.view, 'Must be called from view context'

    values = metadata.view['state']['values']
    leave_type = (
        values['type'][VACATION_TYPE_ACTION_ID]['selected_option']['value']
    )
    date_from = date.fromisoformat(
        values['start'][DATEPICKER_START_ACTION_ID]['selected_date']
    )
    date_to = date.fromisoformat(
        values['end'][DATEPICKER_END_ACTION_ID]['selected_date']
    )
    reason = values['reason'][REASON_INPUT_ACTION_ID].get('value', '')
    return leave_type, date_from, date_to, reason


async def approve_request(
        history: AsyncIOMotorCollection,
        users: AsyncIOMotorCollection,
        request_id: str
) -> None:
    request = await _process_request(history, request_id, 'approved')
    if request:
        await increase_days_by_user(
            users,
            request['leave_type'],
            Decimal(-request['duration']),
            request['user_id'],
        )


async def deny_request(
        history: AsyncIOMotorCollection,
        request_id: str
) -> None:
    await _process_request(history, request_id, 'denied')


async def _process_request(
        collection: AsyncIOMotorCollection,
        request_id: str,
        status: str
) -> Optional[Dict]:
    user = get_current_user_id()
    assert user is not None, 'Must be called from any Slack context'
    assert status in ('approved', 'denied')

    request = await get_request_by_id(collection, request_id)
    if request is None:
        return await send_ephemeral(
            f'Request #`{request_id}` does not exist.'
        )
    elif request['approval_status'] != 'unapproved':
        return await send_ephemeral(
            f'Request #`{request_id}` has already been processed.'
        )

    await update_request_status(collection, request_id, status, user)
    await _send_notification(
        f'{STATUS_EMOJIS[status]} '
        f'Your leave request #`{request_id}` has been {status} by <@{user}>.'
    )

    metadata = action_metadata.get()
    if metadata is not None and metadata.container is not None:
        thread_ts = metadata.container.get('message_ts')
    else:
        thread_ts = None
    await _send_notification(
        f'{STATUS_EMOJIS[status]} '
        f'Request #`{request_id}` has been {status} by <@{user}>.',
        channel_id=ADMIN_CHANNEL,
        thread_ts=thread_ts
    )
    return request


async def get_request_id_from_button() -> str:
    metadata = action_metadata.get()
    assert metadata and metadata.actions, 'Must be called from action context'
    return metadata.actions[0]['value']


async def is_admin_channel() -> bool:
    return get_current_channel_id() == ADMIN_CHANNEL


async def send_history(
        history: AsyncIOMotorCollection,
        users: AsyncIOMotorCollection,
        user: Optional[str] = None,
) -> None:
    current_user = get_current_user_id()
    assert current_user is not None, 'Must be called from any Slack context'

    if user is None:
        user = current_user
    elif user != current_user and not await is_admin_channel():
        return await send_ephemeral(
            'This command is available only in the admin channel.'
        )

    days = await get_days_by_user_id(users, user)
    leaves = await get_leaves_history_by_user_id(history, user)
    blocks = build_days_blocks(days) + build_history_blocks(leaves)
    await send_ephemeral(
        blocks[0]['text']['text'],
        blocks
    )


async def add_days(
        users: AsyncIOMotorCollection,
        leave_type: str,
        days: Decimal,
        user: Optional[str]
) -> None:
    if leave_type not in LEAVE_TYPES:
        return await send_ephemeral(
            f'Leave type must be one of `{"` `".join(LEAVE_TYPES)}`'
        )

    if user:
        await increase_days_by_user(users, leave_type, days, user)
    else:
        await increase_days(users, leave_type, days)
    await send_ephemeral(
        'Amount of available days was increased successfully!'
    )
