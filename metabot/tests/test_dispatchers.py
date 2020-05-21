from typing import Callable, Dict
from unittest.mock import AsyncMock

import pytest

from metabot.lib.dispatchers import CommandDispatcher, ActionDispatcher
from metabot.models.module import Module


@pytest.mark.asyncio
async def test_command_dispatcher_dispatch(
        command_dispatcher: CommandDispatcher,
        module: Module,
        test_command_payload: Callable,
        monkeypatch
) -> None:
    mock = AsyncMock()
    monkeypatch.setattr(command_dispatcher, '_trigger_command', mock)
    command_dispatcher.storage.get_module.return_value = module
    payload = test_command_payload('help me 123')
    await command_dispatcher.dispatch(payload)
    mock.assert_awaited_once_with(
        module,
        module.commands['me'],
        ['123'],
        payload
    )


# noinspection PyProtectedMember
@pytest.mark.asyncio
async def test_command_dispatcher_parse(
        command_dispatcher: CommandDispatcher,
        module: Module,
        test_command_payload: Callable,
) -> None:
    command_dispatcher.storage.get_module.return_value = module
    payload = test_command_payload('help me 123')
    results = await command_dispatcher._parse_payload(payload)
    assert (module, module.commands['me'], ['123']) == results


# noinspection PyProtectedMember
@pytest.mark.asyncio
async def test_command_dispatcher_parse_missing_module_fails(
        command_dispatcher: CommandDispatcher,
        test_command_payload: Callable,
) -> None:
    command_dispatcher.storage.get_module.return_value = None
    payload = test_command_payload('some_module test 123')
    with pytest.raises(ValueError):
        await command_dispatcher._parse_payload(payload)


# noinspection PyProtectedMember
@pytest.mark.parametrize('text', [
    ' ',                # empty command
    'help test 123',    # command doesn't exist
    'help',             # no command name provided
    'help me',          # missing required arguments
])
@pytest.mark.asyncio
async def test_command_dispatcher_parse_fails(
        command_dispatcher: CommandDispatcher,
        module: Module,
        test_command_payload: Callable,
        text: str,
) -> None:
    command_dispatcher.storage.get_module.return_value = module
    payload = test_command_payload(text)
    with pytest.raises(ValueError):
        await command_dispatcher._parse_payload(payload)


@pytest.mark.asyncio
async def test_action_dispatcher_dispatch_actions(
        action_dispatcher: ActionDispatcher,
        test_action_payload: Dict,
        monkeypatch
) -> None:
    mock = AsyncMock()
    monkeypatch.setattr(action_dispatcher, '_trigger_all_actions', mock)

    await action_dispatcher.dispatch(test_action_payload)

    mock.assert_awaited_once_with(
        {'block_actions:action_id', 'block_actions:callback_id'},
        test_action_payload
    )


@pytest.mark.asyncio
async def test_action_dispatcher_dispatch_views(
        action_dispatcher: ActionDispatcher,
        test_view_payload: Dict,
        monkeypatch
) -> None:
    mock = AsyncMock()
    monkeypatch.setattr(action_dispatcher, '_trigger_all_actions', mock)

    await action_dispatcher.dispatch(test_view_payload)

    mock.assert_awaited_once_with(
        {'view_submission:callback_id'},
        test_view_payload
    )


# noinspection PyProtectedMember
@pytest.mark.asyncio
async def test_action_dispatcher_trigger_all_actions(
        action_dispatcher: ActionDispatcher,
        module: Module,
        monkeypatch
) -> None:
    mock = AsyncMock()
    monkeypatch.setattr(action_dispatcher, '_trigger_action', mock)
    action_dispatcher.storage.get_module_by_action.return_value = module

    action_ids = {
        'block_actions:action_id',
        'block_actions:callback_id',
        'view_submission:callback_id'
    }
    payload = {}
    await action_dispatcher._trigger_all_actions(action_ids, payload)

    assert mock.await_count == len(action_ids)
