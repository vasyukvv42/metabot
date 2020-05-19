from typing import Any

import pytest

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
        def func_with_positional_only(a: Any, /, b: Any) -> None:
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
