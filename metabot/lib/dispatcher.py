import logging
from shlex import split
from typing import Dict, Iterable, List

from aiohttp import ClientSession, ClientError, ClientResponseError
from fastapi import FastAPI
from slack import WebClient

from metabot.models.module import Command, Module
from metabot.lib.storage import get_module, get_module_names

log = logging.getLogger(__name__)


class CommandDispatcher:
    session: ClientSession
    slack: WebClient
    command: str

    def __init__(self, app: FastAPI, command: str = '/meta') -> None:
        self.session = app.state.session
        self.slack = app.state.slack
        self.command = command

    async def dispatch(self, payload: Dict[str, str]) -> None:
        parsed_text = split(payload['text'])
        if len(parsed_text) == 0:
            return await self._error(
                payload,
                f'Usage: `{self.command} [module] [command]`. '
                f'Available modules: {self._format_strings(get_module_names())}'
            )
        elif len(parsed_text) == 1:
            parsed_text.append('')  # to trigger empty command

        module_name, command_name, *arguments = parsed_text

        module = get_module(module_name)
        if module is None:
            return await self._error(
                payload,
                f'Module `{module_name}` does not exist. '
                f'Available modules: {self._format_strings(get_module_names())}'
            )

        try:
            command = module.commands[command_name]
        except KeyError:
            return await self._error(
                payload,
                f'Command `{command_name}` in module `{module_name}` '
                f'does not exist. '
                f'Available commands: {self._format_strings(module.commands)}'
            )

        required_arguments = [x for x in command.arguments if not x.is_optional]
        if len(arguments) < len(required_arguments):
            arg_names = (arg.name for arg in required_arguments)
            return await self._error(
                payload,
                f'Missing one or more required arguments for {command_name}. '
                f'Required arguments: {self._format_strings(arg_names)}'
            )

        try:
            await self._trigger_command(module, command, arguments, payload)
        except ClientResponseError:
            log.exception('Module request failed')
        except ClientError:
            log.exception('Module request failed')
            return await self._error(
                payload,
                'Command execution failed. '
                'Please consult with the administrator.'
            )

    async def _trigger_command(
            self,
            module: Module,
            command: Command,
            arguments: List[str],
            metadata: Dict[str, str],
    ) -> None:
        payload = {
            'command': command.name,
            'arguments': {
                arg.name: value
                for arg, value in zip(command.arguments, arguments)
            },
            'metadata': metadata,
        }
        async with self.session.post(module.url, json=payload) as resp:
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
