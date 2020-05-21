import asyncio
import logging
from asyncio import iscoroutinefunction, Task
from dataclasses import dataclass, field
from inspect import signature, Parameter
from typing import Callable, Optional, Dict, List, Any, Type

from fastapi import FastAPI, Depends

from fastapi_metabot.client import (
    AsyncApis,
    ApiClient,
    models
)
from fastapi_metabot.client.exceptions import ApiException
from fastapi_metabot.routes import router
from fastapi_metabot.utils import current_module

log = logging.getLogger(__name__)

Converter = Callable[[str], Any]


@dataclass
class Argument:
    name: str
    is_optional: bool
    type: Type = str  # noqa A003
    description: Optional[str] = None


@dataclass
class Command:
    name: str
    func: Callable
    description: Optional[str] = None
    arguments: List[Argument] = field(default_factory=list)


class Module:
    name: str
    description: Optional[str]
    module_url: str
    metabot_client: ApiClient
    heartbeat_delay: float

    _commands: Dict[str, Command]
    _views: Dict[str, Callable]
    _actions: Dict[str, Callable]
    _converters: Dict[Type, Converter]
    _heartbeat: Optional[Task]

    def __init__(
            self,
            name: str,
            module_url: str,
            metabot_url: str,
            description: Optional[str] = None,
            heartbeat_delay: float = 10,
    ) -> None:
        self.name = name
        self.description = description
        self.module_url = module_url
        self.metabot_client = ApiClient(host=metabot_url)
        self.heartbeat_delay = heartbeat_delay

        self._commands = {}
        self._views = {}
        self._actions = {}
        self._converters = {}
        self._heartbeat = None

    def command(
            self,
            name: str,
            *,
            function: Optional[Callable] = None,
            description: Optional[str] = None,
            arg_descriptions: Optional[Dict[str, str]] = None,
    ) -> Callable:
        assert name not in self._commands, 'Duplicate command names detected'

        def wrapper(f: Callable) -> Callable:
            arguments = self._parse_arguments(f, arg_descriptions)
            self._commands[name] = Command(
                name=name,
                func=f,
                description=description,
                arguments=arguments
            )
            return f

        if function is None:
            return wrapper
        else:
            return wrapper(function)

    def converter(
            self,
            to_type: Type,
            *,
            converter: Optional[Converter] = None,
    ) -> Callable:
        assert to_type not in self._converters, 'Duplicate converters detected'

        def wrapper(f: Callable) -> Callable:
            self._converters[to_type] = f
            return f

        if converter is None:
            return wrapper
        else:
            return wrapper(converter)

    def action(
            self,
            name: str,
            *,
            function: Optional[Callable] = None,
    ) -> Callable:
        assert name not in self._actions, 'Duplicate action names detected'

        def wrapper(f: Callable) -> Callable:
            self._actions[name] = f
            return f

        if function is None:
            return wrapper
        else:
            return wrapper(function)

    def view(
            self,
            name: str,
            *,
            function: Optional[Callable] = None
    ) -> Callable:
        assert name not in self._views, 'Duplicate view names detected'

        def wrapper(f: Callable) -> Callable:
            self._views[name] = f
            return f

        if function is None:
            return wrapper
        else:
            return wrapper(function)

    @staticmethod
    def _parse_arguments(
            f: Callable,
            arg_descriptions: Optional[Dict[str, str]] = None,
    ) -> List[Argument]:
        sig = signature(f)
        params = sig.parameters

        allowed_kind = (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
        assert all(param.kind in allowed_kind for param in params.values()), (
            'Positional-only arguments, *args and **kwargs are not allowed'
        )

        arg_descriptions = arg_descriptions or {}
        return [Argument(
            name=p.name,
            is_optional=p.default is not Parameter.empty,
            type=p.annotation if p.annotation is not Parameter.empty else str,
            description=arg_descriptions.get(p.name),
        ) for p in params.values()]

    async def execute_command(
            self,
            name: str,
            arguments: Dict[str, str],
    ) -> None:
        command = self._commands[name]
        converted_args = {
            arg.name: await self._maybe_await(
                self._get_converter(arg.type),
                value
            )
            for arg in command.arguments
            if (value := arguments.get(arg.name))
        }
        await self._maybe_await(command.func, **converted_args)

    async def execute_action(self, action_id: str) -> None:
        action_type, action_name = action_id.split(':', 2)
        if action_type == 'block_actions':
            await self._maybe_await(self._actions[action_name])
        elif action_type == 'view_submission':
            await self._maybe_await(self._views[action_name])
        else:
            log.error(f'Unknown action {action_id} triggered')

    @staticmethod
    async def _maybe_await(
            function: Callable,
            *args: Any,
            **kwargs: Any
    ) -> Any:
        if iscoroutinefunction(function):
            return await function(*args, **kwargs)
        else:
            return function(*args, **kwargs)

    def _get_converter(self, to_type: Type) -> Converter:
        return self._converters.get(to_type, to_type)

    def install(self, app: FastAPI, prefix: str = '') -> FastAPI:
        async def set_current_module() -> None:
            current_module.set(self)

        app.include_router(
            router,
            prefix=prefix,
            tags=['metabot', self.name],
            dependencies=[Depends(set_current_module)],
        )

        if self.heartbeat_delay:
            app.add_event_handler('startup', self._start_heartbeat)
            app.add_event_handler('shutdown', self._stop_heartbeat)

        return app

    def _start_heartbeat(self) -> None:
        module = self._build_module_payload()
        metabot_api = AsyncApis(self.metabot_client).metabot_api

        async def heartbeat() -> None:
            while True:
                try:
                    await metabot_api.register_module_api_modules_post(module)
                except ApiException:
                    log.exception('Heartbeat to metabot server has failed')

                await asyncio.sleep(self.heartbeat_delay)

        self._heartbeat = asyncio.create_task(heartbeat())

    def _build_module_payload(self) -> models.Module:
        return models.Module(
            name=self.name,
            description=self.description,
            url=self.module_url,
            commands={
                command.name: models.Command(
                    name=command.name,
                    description=command.description,
                    arguments=[
                        models.CommandArgument(
                            name=arg.name,
                            description=arg.description,
                            is_optional=arg.is_optional,
                        ) for arg in command.arguments
                    ],
                ) for command in self._commands.values()
            },
            actions=(
                [f'block_actions:{action}' for action in self._actions]
                + [f'view_submission:{view}' for view in self._views]
            )
        )

    def _stop_heartbeat(self) -> None:
        if self._heartbeat is not None:
            self._heartbeat.cancel()
            self._heartbeat = None
