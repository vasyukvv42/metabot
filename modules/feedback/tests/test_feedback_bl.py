from typing import Dict
from unittest.mock import AsyncMock, ANY, MagicMock

import pytest

from feedback import bl


@pytest.mark.asyncio
async def test_send_ephemeral(monkeypatch) -> None:
    mock = AsyncMock(name='async_slack_request')
    monkeypatch.setattr(bl, 'async_slack_request', mock)

    await bl.send_ephemeral('test')
    mock.assert_awaited_once_with(method='chat_postEphemeral', payload=ANY)


# noinspection PyProtectedMember
@pytest.mark.asyncio
async def test_send_message(monkeypatch) -> None:
    mock = AsyncMock(name='async_slack_request')
    monkeypatch.setattr(bl, 'async_slack_request', mock)

    await bl._send_message('test')
    mock.assert_awaited_once_with(method='chat_postMessage', payload=ANY)


@pytest.mark.asyncio
async def test_open_creation_view(
        test_command_metadata: Dict,
        monkeypatch
) -> None:
    mock_builder = MagicMock(name='build_creation_view')
    view = mock_builder.return_value = {}
    monkeypatch.setattr(bl, 'build_creation_view', mock_builder)

    mock_slack = AsyncMock(name='async_slack_request')
    monkeypatch.setattr(bl, 'async_slack_request', mock_slack)

    await bl.open_creation_view(1)
    mock_slack.assert_awaited_once_with(
        method='views_open',
        payload={
            'trigger_id': test_command_metadata['trigger_id'],
            'view': view
        }
    )


def test_parse_creation_view(test_action_metadata: Dict) -> None:
    title, recipients, questions = bl.parse_creation_view()
    assert title == 'asdasd'
    assert recipients == ['U012HADR6QP']
    assert questions == ['Test?' for _ in range(10)]
