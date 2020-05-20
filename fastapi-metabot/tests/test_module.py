from asyncio import Task, sleep
from typing import Any
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi.encoders import jsonable_encoder

from fastapi_metabot.client.api.metabot_api import AsyncMetabotApi
from fastapi_metabot.module import Module, Command


def test_add_command(module: Module) -> None:
    name = 'test'
    description = 'description'

    @module.command(
        name,
        description=description,
    )
    async def test() -> None:
        pass

    command = module._commands[name]  # noqa
    assert isinstance(command, Command)
    assert command.name == name
    assert command.description == description
    assert command.func == test

    with pytest.raises(AssertionError):
        module.command(name, function=test, description=description)


def test_add_converter(module: Module) -> None:
    assert module._get_converter(int) == int  # noqa

    @module.converter(int)
    def convert_binary(binary_number: str) -> int:
        return int(binary_number, 2)

    assert module._get_converter(int) == convert_binary  # noqa

    with pytest.raises(AssertionError):
        module.converter(int, converter=convert_binary)


def test_add_action(module: Module) -> None:
    name = 'test'

    @module.action(name)
    async def action() -> None:
        pass

    assert module._actions[name] == action  # noqa

    with pytest.raises(AssertionError):
        module.action(name, function=action)


def test_add_view(module: Module) -> None:
    name = 'test'

    @module.view(name)
    async def view() -> None:
        pass

    assert module._views[name] == view  # noqa

    with pytest.raises(AssertionError):
        module.view(name, function=view)


def test_parse_arguments_fails() -> None:
    with pytest.raises(AssertionError):
        def func_with_args(*args: Any) -> None:
            pass

        Module._parse_arguments(func_with_args)  # noqa

    with pytest.raises(AssertionError):
        def func_with_kwargs(**kwargs: Any) -> None:
            pass

        Module._parse_arguments(func_with_kwargs)  # noqa

    with pytest.raises(AssertionError):
        def func_with_positional_only(a: Any, /, b: Any) -> None:  # noqa E225
            pass

        Module._parse_arguments(func_with_positional_only)  # noqa


def test_parse_arguments() -> None:
    async def func(arg1: str, arg2: int = 1) -> None:
        pass

    descriptions = {
        'arg1': 'HELLOOOOOOOOO'
    }
    required, optional = Module._parse_arguments(func, descriptions)  # noqa

    assert required.is_optional is False
    assert required.type == str
    assert required.name == 'arg1'
    assert required.description == descriptions['arg1']

    assert optional.is_optional is True
    assert optional.type == int
    assert optional.name == 'arg2'
    assert optional.description is None


@pytest.mark.asyncio
async def test_execute_command(module: Module) -> None:
    name = 'test'
    mock = MagicMock(name='func')

    @module.command(name)
    def func(arg: str) -> None:
        pass

    module._commands[name].func = mock  # noqa
    await module.execute_command(name, {'arg': 'test'})
    mock.assert_called_once_with(arg='test')


@pytest.mark.asyncio
async def test_execute_command_async(module: Module) -> None:
    name = 'test'
    mock = AsyncMock(name='func')

    @module.command(name)
    async def func(arg: str) -> None:
        pass

    module._commands[name].func = mock  # noqa
    await module.execute_command(name, {'arg': 'test'})
    mock.assert_awaited_once_with(arg='test')


@pytest.mark.asyncio
async def test_execute_action(module: Module) -> None:
    name = 'action'
    mock = MagicMock(name='action')
    module.action(name, function=mock)

    await module.execute_action(f'block_actions:{name}')
    mock.assert_called_once()


@pytest.mark.asyncio
async def test_execute_action_async(module: Module) -> None:
    name = 'action'
    mock = AsyncMock(name='action')
    module.action(name, function=mock)

    await module.execute_action(f'block_actions:{name}')
    mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_view(module: Module) -> None:
    name = 'view'
    mock = MagicMock(name='view')
    module.view(name, function=mock)

    await module.execute_action(f'view_submission:{name}')
    mock.assert_called_once()


@pytest.mark.asyncio
async def test_execute_view_async(module: Module) -> None:
    name = 'view'
    mock = AsyncMock(name='view')
    module.view(name, function=mock)

    await module.execute_action(f'view_submission:{name}')
    mock.assert_awaited_once()


def test_build_module_payload(module: Module) -> None:
    command_name = 'command'
    description = 'description'
    action_name = 'action'
    view_name = 'view'

    @module.command(
        command_name,
        description=description,
        arg_descriptions={
            'req': description
        }
    )
    def command(req: str, opt: str = '') -> None:
        pass

    @module.action(action_name)
    def action() -> None:
        pass

    @module.view(view_name)
    def view() -> None:
        pass

    payload = jsonable_encoder(module._build_module_payload())  # noqa
    assert payload == {
        'name': module.name,
        'description': module.description,
        'url': module.module_url,
        'commands': {
            command_name: {
                'name': command_name,
                'description': description,
                'arguments': [
                    {
                        'name': 'req',
                        'is_optional': False,
                        'description': description
                    },
                    {
                        'name': 'opt',
                        'is_optional': True,
                        'description': None
                    },
                ]
            }
        },
        'actions': [
            f'block_actions:{action_name}',
            f'view_submission:{view_name}',
        ]
    }


@pytest.mark.asyncio
async def test_hearbeat(module: Module, monkeypatch) -> None:
    payload = module._build_module_payload()  # noqa
    mock_api = AsyncMock(name='register_module_api_modules_post')

    monkeypatch.setattr(
        AsyncMetabotApi,
        'register_module_api_modules_post',
        mock_api
    )

    module._start_heartbeat()  # noqa
    assert isinstance(module._heartbeat, Task)  # noqa
    await sleep(0)
    mock_api.assert_awaited_with(payload)

    module._stop_heartbeat()  # noqa
    assert module._heartbeat is None  # noqa
