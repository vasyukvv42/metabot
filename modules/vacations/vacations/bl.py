import logging
from datetime import date
from typing import Dict, Optional, List, Tuple

from motor.motor_asyncio import AsyncIOMotorCollection  # noqa

from fastapi_metabot.client import ApiClient, AsyncApis
from fastapi_metabot.client.models import SlackRequest
from fastapi_metabot.utils import (
    get_current_user_id,
    get_current_channel_id,
    command_metadata,
    action_metadata,
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
    ADMIN_CHANNEL
)
from vacations.db import (
    save_request,
    update_request_status,
    get_request_by_id,
    get_request_history_by_user_id
)

log = logging.getLogger(__name__)


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
    assert user is not None, 'Must be called from any Slack context'
    blocks = build_admin_request_notification(
        date_from, date_to, reason, request_id, user
    )
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
    user = await get_current_user_id()
    assert user is not None, 'Must be called from any Slack context'

    if date_to is None:
        date_to = date_from

    if date_from > date_to:
        date_to, date_from = date_from, date_to

    if date_from < date.today():
        return await send_ephemeral(
            metabot_client,
            'Start date of your leave must be today or in the future.'
        )

    request_id = await save_request(
        collection,
        date_from,
        date_to,
        reason,
        user
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


async def open_request_view(metabot_client: ApiClient) -> None:
    metadata = command_metadata.get()
    assert metadata is not None, 'Must be called from command context'

    api = AsyncApis(metabot_client).metabot_api
    await api.request_api_slack_post(
        SlackRequest(
            method='views_open',
            payload={
                'trigger_id': metadata.trigger_id,
                'view': build_request_view()
            }
        )
    )


async def parse_request_view() -> Tuple[date, date, str]:
    metadata = action_metadata.get()
    assert metadata and metadata.view, 'Must be called from view context'

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
    user = await get_current_user_id()
    assert user is not None, 'Must be called from any Slack context'
    assert status in ('approved', 'denied')

    request = await get_request_by_id(collection, request_id)
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

    await update_request_status(collection, request_id, status, user)
    await _send_notification(
        metabot_client,
        f'{STATUS_EMOJIS[status]} '
        f'Your leave request #`{request_id}` has been {status} by <@{user}>.'
    )

    metadata = action_metadata.get()
    if metadata is not None and metadata.container is not None:
        thread_ts = metadata.container.get('message_ts')
    else:
        thread_ts = None
    await _send_notification(
        metabot_client,
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
    return await get_current_channel_id() == ADMIN_CHANNEL


async def send_history(
        collection: AsyncIOMotorCollection,
        metabot_client: ApiClient,
        user: Optional[str] = None
) -> None:
    current_user = await get_current_user_id()
    assert current_user is not None, 'Must be called from any Slack context'

    if user is None:
        user = current_user
    elif user != current_user and not await is_admin_channel():
        return await send_ephemeral(
            metabot_client,
            'This command is available only in the admin channel.'
        )

    history = await get_request_history_by_user_id(collection, user)
    blocks = build_history_blocks(history, user)
    await send_ephemeral(
        metabot_client,
        blocks[0]['text']['text'],
        blocks
    )
