from datetime import date
from decimal import Decimal
from typing import Dict
from unittest.mock import AsyncMock, ANY, MagicMock

import pytest

from vacations import bl


@pytest.mark.asyncio
async def test_send_ephemeral(monkeypatch) -> None:
    mock = AsyncMock(name='async_slack_request')
    monkeypatch.setattr(bl, 'async_slack_request', mock)

    await bl.send_ephemeral('test')
    mock.assert_awaited_once_with(method='chat_postEphemeral', payload=ANY)


# noinspection PyProtectedMember
@pytest.mark.asyncio
async def test_send_notification(monkeypatch) -> None:
    mock = AsyncMock(name='async_slack_request')
    monkeypatch.setattr(bl, 'async_slack_request', mock)

    await bl._send_notification('test')
    mock.assert_awaited_once_with(method='chat_postMessage', payload=ANY)


# noinspection PyProtectedMember
@pytest.mark.asyncio
async def test_notify_admins(monkeypatch, test_command_metadata: Dict) -> None:
    mock_builder = MagicMock(name='build_admin_request_notification')
    blocks = mock_builder.return_value = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': 'some text'
            }
        }
    ]
    monkeypatch.setattr(bl, 'build_admin_request_notification', mock_builder)

    mock_notification = AsyncMock(name='build_admin_request_notification')
    monkeypatch.setattr(bl, '_send_notification', mock_notification)

    await bl._notify_admins(
        'vacation',
        date.today(),
        date.today(),
        1,
        10,
        'reason',
        'asdasdasd'
    )
    mock_builder.assert_called_once()
    mock_notification.assert_awaited_once_with(
        blocks[0]['text']['text'],
        blocks,
        bl.ADMIN_CHANNEL
    )


@pytest.mark.asyncio
async def test_open_request_view(
        test_command_metadata: Dict,
        monkeypatch
) -> None:
    mock_get_days = AsyncMock(name='get_days_by_user_id')
    monkeypatch.setattr(bl, 'get_days_by_user_id', mock_get_days)

    mock_builder = MagicMock(name='build_request_view')
    view = mock_builder.return_value = {}
    monkeypatch.setattr(bl, 'build_request_view', mock_builder)

    mock_slack = AsyncMock(name='async_slack_request')
    monkeypatch.setattr(bl, 'async_slack_request', mock_slack)

    await bl.open_request_view(None)
    mock_slack.assert_awaited_once_with(
        method='views_open',
        payload={
            'trigger_id': test_command_metadata['trigger_id'],
            'view': view
        }
    )


def test_parse_request_view(test_action_metadata: Dict) -> None:
    leave_type, date_from, date_to, reason = bl.parse_request_view()
    assert leave_type == 'test'
    assert date_from == date(2020, 10, 31)
    assert date_to == date(2020, 10, 31)
    assert reason == 'asdasd'


@pytest.mark.asyncio
async def test_approve_request(monkeypatch, test_request: Dict) -> None:
    mock_process = AsyncMock(name='_process_request')
    mock_process.return_value = test_request
    monkeypatch.setattr(bl, '_process_request', mock_process)

    mock_increase = AsyncMock(name='increase_days_by_user')
    monkeypatch.setattr(bl, 'increase_days_by_user', mock_increase)

    request_id = '123'
    users = 'users'
    history = 'history'
    await bl.approve_request(history, users, request_id)

    mock_process.assert_awaited_once_with(history, request_id, 'approved')
    mock_increase.assert_awaited_once_with(
        users,
        test_request['leave_type'],
        Decimal(-test_request['duration']),
        test_request['user_id']
    )


@pytest.mark.asyncio
async def test_deny_request(monkeypatch) -> None:
    mock_process = AsyncMock(name='_process_request')
    monkeypatch.setattr(bl, '_process_request', mock_process)

    request_id = '123'
    history = 'history'
    await bl.deny_request(history, request_id)

    mock_process.assert_awaited_once_with(history, request_id, 'denied')


@pytest.mark.asyncio
async def test_create_request_invalid_leave_type_fails(
        test_command_metadata: Dict,
        monkeypatch
) -> None:
    mock = AsyncMock(name='send_ephemeral')
    monkeypatch.setattr(bl, 'send_ephemeral', mock)
    await bl.create_request(None, None, 'asd', None, None, '')
    mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_request(
        test_command_metadata: Dict,
        monkeypatch
) -> None:
    mock_get_days = AsyncMock(name='get_days_by_user_id')
    monkeypatch.setattr(bl, 'get_days_by_user_id', mock_get_days)

    mock_save = AsyncMock(name='save_request')
    mock_save.return_value = '123asd'
    monkeypatch.setattr(bl, 'save_request', mock_save)

    mock_send = AsyncMock(name='_send_notification')
    monkeypatch.setattr(bl, '_send_notification', mock_send)

    mock_notify = AsyncMock(name='_notify_admins')
    monkeypatch.setattr(bl, '_notify_admins', mock_notify)

    users = 'users'
    history = 'history'
    await bl.create_request(
        history,
        users,
        'test',
        date.today(),
        date.today(),
        ''
    )

    mock_get_days.assert_awaited_once()
    mock_save.assert_awaited_once()
    mock_send.assert_awaited_once()
    mock_notify.assert_awaited_once()


# noinspection PyProtectedMember
@pytest.mark.asyncio
async def test_process_request(
        test_action_metadata: Dict,
        test_request: Dict,
        monkeypatch
) -> None:
    mock_get_request = AsyncMock(name='get_request_by_id')
    mock_get_request.return_value = test_request
    monkeypatch.setattr(bl, 'get_request_by_id', mock_get_request)

    mock_update = AsyncMock(name='update_request_status')
    monkeypatch.setattr(bl, 'update_request_status', mock_update)

    mock_send = AsyncMock(name='_send_notification')
    monkeypatch.setattr(bl, '_send_notification', mock_send)

    await bl._process_request(None, test_request['_id'], 'approved')

    mock_update.assert_awaited_once()
    assert mock_send.await_count == 2
