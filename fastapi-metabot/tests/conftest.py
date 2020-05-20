from typing import Iterable, Dict
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from requests import Session
from starlette.background import BackgroundTasks
from starlette.testclient import TestClient

from fastapi_metabot.models import ActionMetadata, CommandMetadata
from fastapi_metabot.module import Module
from fastapi_metabot.routes import router
from fastapi_metabot.utils import (
    action_metadata,
    command_metadata,
    current_module,
)


@pytest.fixture
def module() -> Module:
    return Module(
        name='example',
        description='Example module',
        module_url='http://localhost:8000',
        metabot_url='http://localhost:8000',
        heartbeat_delay=0,
    )


@pytest.fixture
def set_current_module(module: Module) -> Module:
    token = current_module.set(module)
    yield module
    current_module.reset(token)


@pytest.fixture
def app(module: Module) -> FastAPI:
    app = FastAPI()
    module.install(app)
    app.include_router(router, prefix='/fake')
    return app


@pytest.fixture
def test_client(app: FastAPI) -> Iterable[Session]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_command_metadata() -> Dict:
    metadata = {
        'token': 'ASD123',
        'command': '/meta',
        'response_url': 'https://localhost/',
        'trigger_id': '123456.123456',
        'user_id': 'U012HADR6QP',
        'user_name': 'v.vasyuk',
        'channel_id': 'C012Y8P7KC3',
        'text': 'example test test',
    }
    token = command_metadata.set(CommandMetadata(**metadata))
    yield metadata
    command_metadata.reset(token)


@pytest.fixture
def test_action_metadata() -> Dict:
    metadata = {
        'type': 'block_actions',
        'user': {'id': 'U012HADR6QP'},
        'channel': {'id': 'C012Y8P7KC3'},
    }
    token = action_metadata.set(ActionMetadata(**metadata))
    yield metadata
    action_metadata.reset(token)


@pytest.fixture
def mock_background_tasks(monkeypatch) -> MagicMock:
    mock = MagicMock(name='add_task')
    monkeypatch.setattr(BackgroundTasks, 'add_task', mock)
    return mock
