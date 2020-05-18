import logging
from datetime import date
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
    STATUS_EMOJIS
)
from vacations.config import (
    DATEPICKER_START_ACTION_ID,
    DATEPICKER_END_ACTION_ID,
    REASON_INPUT_ACTION_ID,
    ADMIN_CHANNEL, VACATION_TYPES, VACATION_TYPE_ACTION_ID
)
from vacations.db import (
    save_request,
    update_request_status,
    get_request_by_id,
    get_request_history_by_user_id
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
        request_type: str,
        date_from: date,
        date_to: date,
        reason: str,
        request_id: str
) -> None:
    user = get_current_user_id()
    assert user is not None, 'Must be called from any Slack context'
    blocks = build_admin_request_notification(
        request_type, date_from, date_to, reason, request_id, user
    )
    await _send_notification(
        blocks[0]['text']['text'],
        blocks,
        ADMIN_CHANNEL
    )


async def create_request(
        collection: AsyncIOMotorCollection,
        request_type: str,
        date_from: Optional[date],
        date_to: Optional[date],
        reason: str,
) -> None:
    user = get_current_user_id()
    assert user is not None, 'Must be called from any Slack context'

    if request_type not in VACATION_TYPES:
        return await send_ephemeral(
            f'Request type must be one of `{"` `".join(VACATION_TYPES)}`'
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

    request_id = await save_request(
        collection,
        request_type,
        date_from,
        date_to,
        reason,
        user,
    )
    await _send_notification(
        f'Leave request #`{request_id}` has been created! '
        f'You will be notified when your request is approved or denied.'
    )
    await _notify_admins(
        request_type,
        date_from,
        date_to,
        reason,
        request_id
    )


async def open_request_view() -> None:
    metadata = command_metadata.get()
    assert metadata is not None, 'Must be called from command context'

    await async_slack_request(
        method='views_open',
        payload={
            'trigger_id': metadata.trigger_id,
            'view': build_request_view()
        }
    )


async def parse_request_view() -> Tuple[str, date, date, str]:
    metadata = action_metadata.get()
    assert metadata and metadata.view, 'Must be called from view context'

    values = metadata.view['state']['values']
    request_type = (
        values['type'][VACATION_TYPE_ACTION_ID]['selected_option']['value']
    )
    date_from = date.fromisoformat(
        values['start'][DATEPICKER_START_ACTION_ID]['selected_date']
    )
    date_to = date.fromisoformat(
        values['end'][DATEPICKER_END_ACTION_ID]['selected_date']
    )
    reason = values['reason'][REASON_INPUT_ACTION_ID].get('value', '')
    return request_type, date_from, date_to, reason


async def process_request(
        collection: AsyncIOMotorCollection,
        request_id: str,
        status: str
) -> None:
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


async def get_request_id_from_button() -> str:
    metadata = action_metadata.get()
    assert metadata and metadata.actions, 'Must be called from action context'
    return metadata.actions[0]['value']


async def is_admin_channel() -> bool:
    return get_current_channel_id() == ADMIN_CHANNEL


async def send_history(
        collection: AsyncIOMotorCollection,
        user: Optional[str] = None
) -> None:
    current_user = get_current_user_id()
    assert current_user is not None, 'Must be called from any Slack context'

    if user is None:
        user = current_user
    elif user != current_user and not await is_admin_channel():
        return await send_ephemeral(
            'This command is available only in the admin channel.'
        )

    history = await get_request_history_by_user_id(collection, user)
    blocks = build_history_blocks(history, user)
    await send_ephemeral(
        blocks[0]['text']['text'],
        blocks
    )
