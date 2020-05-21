from typing import Dict
from unittest.mock import MagicMock

from requests import Session

from fastapi_metabot.module import Module


def test_commands_route(
        module: Module,
        test_client: Session,
        mock_background_tasks: MagicMock,
        test_command_metadata: Dict,
) -> None:
    name = 'test'

    @module.command(name)
    async def func(arg: str) -> None:
        pass

    args = {'arg': 'test'}
    response = test_client.post(f'/commands/{name}', json={
        'arguments': args,
        'metadata': test_command_metadata,
    })
    assert response.status_code == 200
    mock_background_tasks.assert_called_once_with(
        module.execute_command,
        name,
        args
    )


def test_actions_route_action(
        module: Module,
        test_client: Session,
        mock_background_tasks: MagicMock,
        test_action_metadata: Dict,
) -> None:
    name = 'test'
    full_name = f'block_actions:{name}'

    @module.action(name)
    async def func(arg: str) -> None:
        pass

    response = test_client.post(f'/actions/{full_name}', json={
        'metadata': test_action_metadata,
    })
    assert response.status_code == 200
    mock_background_tasks.assert_called_once_with(
        module.execute_action,
        full_name
    )


def test_actions_route_view(
        module: Module,
        test_client: Session,
        mock_background_tasks: MagicMock,
        test_action_metadata: Dict,
) -> None:
    name = 'test'
    full_name = f'view_submission:{name}'

    @module.view(name)
    async def func(arg: str) -> None:
        pass

    response = test_client.post(f'/actions/{full_name}', json={
        'metadata': test_action_metadata,
    })
    assert response.status_code == 200
    mock_background_tasks.assert_called_once_with(
        module.execute_action,
        full_name
    )


def test_commands_route_empty_module_500(
        test_command_metadata: Dict,
        test_client: Session,
) -> None:
    response = test_client.post('/fake/commands/test', json={
        'arguments': {},
        'metadata': test_command_metadata,
    })
    assert response.status_code == 500


def test_actions_route_empty_module_500(
        test_action_metadata: Dict,
        test_client: Session,
) -> None:
    response = test_client.post('/fake/actions/test', json={
        'metadata': test_action_metadata,
    })
    assert response.status_code == 500
