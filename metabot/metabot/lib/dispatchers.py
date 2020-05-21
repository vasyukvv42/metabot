import asyncio
import logging
from shlex import split
from typing import Dict, Tuple, List, Iterable, Any, Set

from aiohttp import ClientSession, ClientError
from fastapi import FastAPI
from slack import WebClient

from metabot.lib.storage import Storage
from metabot.models.module import Module, Command

log = logging.getLogger(__name__)


class ActionDispatcher:
    session: ClientSession
    storage: Storage

    def __init__(self, app: FastAPI) -> None:
        self.session = app.state.session
        self.storage = app.state.storage

    async def dispatch(self, payload: Dict[str, Any]) -> None:
        action_ids = set()

        if actions := payload.get('actions'):
            action_ids |= {
                f'{payload["type"]}:{action["action_id"]}'
                for action in actions
            }

        if action_callback_id := payload.get('callback_id'):
            action_ids.add(f'{payload["type"]}:{action_callback_id}')

        if view := payload.get('view'):
            if view_callback_id := view.get("callback_id"):
                action_ids.add(f'{payload["type"]}:{view_callback_id}')

        await self._trigger_all_actions(action_ids, payload)

    async def _trigger_all_actions(
            self,
            action_ids: Set[str],
            payload: Dict[str, Any],
    ) -> None:
        futures = []
        for action_id in action_ids:
            module = await self.storage.get_module_by_action(action_id)
            if module is not None:
                futures.append(
                    self._trigger_action(module, action_id, payload)
                )
        await asyncio.gather(*futures)

    async def _trigger_action(
            self,
            module: Module,
            action_id: str,
            metadata: Dict[str, Any]
    ) -> None:
        payload = {
            'metadata': metadata,
        }
        url = f'{module.url}/actions/{action_id}'
        async with self.session.post(url, json=payload) as resp:
            resp.raise_for_status()


class CommandDispatcher:
    session: ClientSession
    slack: WebClient
    storage: Storage

    def __init__(self, app: FastAPI) -> None:
        self.session = app.state.session
        self.slack = app.state.slack
        self.storage = app.state.storage

    async def dispatch(self, payload: Dict[str, str]) -> None:
        try:
            module, command, arguments = await self._parse_payload(payload)
        except ValueError as e:
            return await self._error(
                payload,
                str(e)
            )

        try:
            await self._trigger_command(module, command, arguments, payload)
        except ClientError:
            log.exception('Module request failed')
            await self._error(
                payload,
                'Command execution failed. '
                'Please consult with the administrator.'
            )

    async def _parse_payload(
            self,
            payload: Dict[str, str],
    ) -> Tuple[Module, Command, List[str]]:
        parsed_text = split(payload['text'])
        if len(parsed_text) == 0:
            formatted_modules = self._format_strings(
                await self.storage.get_module_names()
            )
            raise ValueError(
                f'Usage: `{payload["command"]} [module] [command]`. '
                f'Available modules: {formatted_modules}'
            )
        elif len(parsed_text) == 1:
            parsed_text.append('')

        module_name, command_name, *arguments = parsed_text

        module = await self.storage.get_module(module_name)
        if module is None:
            formatted_modules = self._format_strings(
                await self.storage.get_module_names()
            )
            raise ValueError(
                f'Module `{module_name}` does not exist. '
                f'Available modules: {formatted_modules}'
            )

        try:
            command = module.commands[command_name]
        except KeyError:
            raise ValueError(
                f'Usage: `{payload["command"]} {module_name} [command]`. '
                f'Available commands: {self._format_strings(module.commands)}'
            )

        required_arguments = [x for x in command.arguments if not x.is_optional]
        if len(arguments) < len(required_arguments):
            arg_names = (arg.name for arg in required_arguments)
            raise ValueError(
                f'Missing one or more required arguments for {command_name}. '
                f'Required arguments: {self._format_strings(arg_names)}'
            )

        return module, command, arguments

    async def _trigger_command(
            self,
            module: Module,
            command: Command,
            arguments: List[str],
            metadata: Dict[str, str],
    ) -> None:
        payload = {
            'arguments': {
                arg.name: value
                for arg, value in zip(command.arguments, arguments)
            },
            'metadata': metadata,
        }
        url = f'{module.url}/commands/{command.name}'
        async with self.session.post(url, json=payload) as resp:
            resp.raise_for_status()

    async def _error(self, payload: Dict[str, str], message: str) -> None:
        channel = payload['channel_id']
        user = payload['user_id']
        log.info(
            f'Error triggered by user {user} in channel {channel}. '
            f'Sending ephemeral error message: {message}'
        )
        await self.slack.chat_postEphemeral(
            channel=channel,
            user=user,
            text=message,
        )

    @staticmethod
    def _format_strings(strings: Iterable[str]) -> str:
        return ' '.join(f'`{x}`' for x in strings)
