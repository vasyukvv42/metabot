from typing import Dict
from unittest.mock import MagicMock, AsyncMock

import pytest

from fastapi_metabot.client.api.metabot_api import SyncMetabotApi, \
    AsyncMetabotApi
from fastapi_metabot.client.models import SlackRequest
from fastapi_metabot.module import Module
from fastapi_metabot.utils import (
    get_current_user_id,
    get_current_channel_id,
    slack_request,
    async_slack_request,
)


def test_get_current_user_id_command(
        test_command_metadata: Dict,
) -> None:
    user_id = get_current_user_id()
    assert user_id == test_command_metadata['user_id']


def test_get_current_user_id_action(
        test_action_metadata: Dict,
) -> None:
    user_id = get_current_user_id()
    assert user_id == test_action_metadata['user']['id']


def test_get_current_user_id_no_context() -> None:
    user_id = get_current_user_id()
    assert user_id is None


def test_get_current_channel_id_command(
        test_command_metadata: Dict,
) -> None:
    channel_id = get_current_channel_id()
    assert channel_id == test_command_metadata['channel_id']


def test_get_current_channel_id_action(
        test_action_metadata: Dict,
) -> None:
    channel_id = get_current_channel_id()
    assert channel_id == test_action_metadata['channel']['id']


def test_get_current_channel_id_no_context() -> None:
    channel_id = get_current_channel_id()
    assert channel_id is None


def test_slack_request(set_current_module: Module, monkeypatch) -> None:
    mock_api = MagicMock(name='request_api_slack_post')
    monkeypatch.setattr(
        SyncMetabotApi,
        'request_api_slack_post',
        mock_api
    )

    method = 'chat_postMessage'
    payload = {'text': 'test', 'channel': '#general'}

    slack_request(method, payload)
    mock_api.assert_called_once_with(SlackRequest(
        method=method,
        payload=payload,
    ))


@pytest.mark.asyncio
async def test_async_slack_request(
        set_current_module: Module,
        monkeypatch
) -> None:
    mock_api = AsyncMock(name='request_api_slack_post')
    monkeypatch.setattr(
        AsyncMetabotApi,
        'request_api_slack_post',
        mock_api
    )

    method = 'chat_postMessage'
    payload = {'text': 'test', 'channel': '#general'}

    await async_slack_request(method, payload)
    mock_api.assert_awaited_once_with(SlackRequest(
        method=method,
        payload=payload,
    ))
