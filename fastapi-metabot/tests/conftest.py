from typing import Iterable

import pytest
from fastapi import FastAPI
from requests import Session
from starlette.testclient import TestClient

from fastapi_metabot.module import Module


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
def app(module: Module) -> FastAPI:
    app = FastAPI()
    module.install(app)
    return app


@pytest.fixture
def test_client(app: FastAPI) -> Iterable[Session]:
    with TestClient(app) as client:
        yield client
