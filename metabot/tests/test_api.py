from typing import Dict
from unittest.mock import AsyncMock

from fastapi import FastAPI
from requests import Session

from metabot.api.routes import slack
from metabot.models.module import Module
from metabot.models.slack import SlackRequest


def test_slack_request_invalid_method_fails(test_client: Session) -> None:
    resp = test_client.post('/api/slack/', json={
        'method': 'sereda_medok',
        'payload': {}
    })
    assert resp.status_code == 422


def test_slack_request(
        app: FastAPI,
        test_client: Session,
        monkeypatch
) -> None:
    class MockSlackResponse:
        @property
        def data(self) -> Dict:
            return {'ok': True}

    mock = AsyncMock(name='slack_request', return_value=MockSlackResponse())
    monkeypatch.setattr(slack, 'slack_request', mock)
    payload = {
        'method': 'chat_postMessage',
        'payload': {'text': 'test', 'channel': '#general'}
    }

    resp = test_client.post('/api/slack/', json=payload)

    mock.assert_awaited_once_with(app.state.slack, SlackRequest(**payload))

    assert resp.status_code == 200
    assert resp.json() == {'data': mock.return_value.data}


def test_get_all_modules(
        test_client: Session,
        app: FastAPI,
        module: Module,
        monkeypatch
) -> None:
    mock = AsyncMock(name='get_all_modules', return_value={module.name: module})
    monkeypatch.setattr(app.state.storage, 'get_all_modules', mock)

    resp = test_client.get('/api/modules/')
    assert resp.status_code == 200
    assert resp.json() == {
        'modules': {module.name: module.dict()}
    }

    mock.assert_awaited_once_with()


def test_get_module_by_name_404(test_client: Session) -> None:
    resp = test_client.get('/api/modules/kek')
    assert resp.status_code == 404


def test_get_module_by_name(
        test_client: Session,
        app: FastAPI,
        module: Module,
        monkeypatch
) -> None:
    mock = AsyncMock(name='get_module', return_value=module)
    monkeypatch.setattr(app.state.storage, 'get_module', mock)

    resp = test_client.get('/api/modules/help')
    assert resp.status_code == 200
    assert resp.json() == module.dict()

    mock.assert_awaited_once_with(module.name)


def test_register_module(
        test_client: Session,
        app: FastAPI,
        module: Module,
        monkeypatch
) -> None:
    mock = AsyncMock(name='add_or_replace_module')
    monkeypatch.setattr(app.state.storage, 'add_or_replace_module', mock)

    resp = test_client.post('/api/modules/', json=module.dict())
    assert resp.status_code == 200
    assert resp.json() == module.dict()

    mock.assert_awaited_once_with(module)
