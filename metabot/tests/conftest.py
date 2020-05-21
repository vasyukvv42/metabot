from typing import Iterable, Dict, Callable
from unittest.mock import AsyncMock

import aioredis
import mockaioredis
import pytest
from fastapi import FastAPI
from requests import Session
from starlette.testclient import TestClient
from starlette.config import environ

environ['SLACK_SIGNING_SECRET'] = 'test'
environ['SLACK_API_TOKEN'] = 'test'
environ['REDIS_URL'] = 'redis://localhost'

from metabot.models.module import Module  # noqa E402
from metabot.lib.dispatchers import CommandDispatcher, ActionDispatcher  # noqa E402


@pytest.fixture
def redis(monkeypatch) -> None:
    monkeypatch.setattr(
        aioredis,
        'create_redis_pool',
        mockaioredis.create_redis_pool
    )


@pytest.fixture
def app(redis) -> FastAPI:
    from metabot.main import app
    return app


@pytest.fixture
def test_client(app: FastAPI) -> Iterable[Session]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def module() -> Module:
    return Module(**{
        'name': 'help',
        'description': 'Help module',
        'url': 'http://help-module:8000',
        'commands': {
            'me': {
                'name': 'me',
                'description': 'Get help',
                'arguments': [
                    {
                        'name': 'module_name',
                        'is_optional': False,
                        'description': 'Module name'
                    }
                ]
            }
        },
        'actions': [],
    })


@pytest.fixture
def test_command_payload() -> Callable:
    def create_payload(text: str) -> Dict:
        return {
            'command': '/meta',
            'text': text,
            'channel_id': 'C012Y8P7KC3',
            'user_id': 'U012HADR6QP',
        }

    return create_payload


@pytest.fixture
def test_action_payload() -> Dict:
    return {
        'type': 'block_actions',
        'callback_id': 'callback_id',
        'actions': [
            {'action_id': 'action_id'}
        ]
    }


@pytest.fixture
def test_view_payload() -> Dict:
    return {
        'type': 'view_submission',
        'view': {
            'callback_id': 'callback_id'
        }
    }


@pytest.fixture
def command_dispatcher() -> CommandDispatcher:
    return CommandDispatcher(AsyncMock())


@pytest.fixture
def action_dispatcher() -> ActionDispatcher:
    return ActionDispatcher(AsyncMock())
