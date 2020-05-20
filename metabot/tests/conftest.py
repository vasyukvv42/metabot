from typing import Iterable

import aioredis
import mockaioredis
import pytest
from fastapi import FastAPI
from requests import Session
from starlette.testclient import TestClient

from metabot.models.module import Module, SAMPLE_MODULE


@pytest.fixture
def redis(monkeypatch) -> None:
    monkeypatch.setattr(
        aioredis,
        'create_redis_pool',
        mockaioredis.create_redis_pool
    )


@pytest.fixture
def test_configs(monkeypatch) -> None:
    monkeypatch.setenv('SLACK_SIGNING_SECRET', 'test')
    monkeypatch.setenv('SLACK_API_TOKEN', 'test')
    monkeypatch.setenv('REDIS_URL', 'redis://localhost')


@pytest.fixture
def app(redis, test_configs) -> FastAPI:
    from metabot.main import app
    return app


@pytest.fixture
def test_client(app: FastAPI) -> Iterable[Session]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def module() -> Module:
    return Module(**SAMPLE_MODULE)
