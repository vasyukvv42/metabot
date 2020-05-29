from typing import Dict

import pytest
from starlette.config import environ

from fastapi_metabot.models import CommandMetadata, ActionMetadata
from fastapi_metabot.module import Module
from fastapi_metabot.utils import command_metadata, action_metadata

environ._has_been_read = set()
environ['HEARTBEAT_DELAY'] = '0'
environ['METABOT_URL'] = 'http://localhost'
environ['MODULE_URL'] = 'http://localhost'
environ['MONGODB_URI'] = 'mongodb://localhost:27017'

from feedback.config import (
    TITLE_INPUT_ACTION_ID,
    RECIPIENTS_SELECT_ACTION_ID,
    QUESTION_INPUT_ACTION_ID,
)


@pytest.fixture
def module() -> Module:
    from feedback.main import module
    return module


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
        'view': {
            'state': {
                'values': {
                    'title': {
                        TITLE_INPUT_ACTION_ID: {
                            'value': 'asdasd'
                        }
                    },
                    'recipients': {
                        RECIPIENTS_SELECT_ACTION_ID: {
                            'selected_users': ['U012HADR6QP']
                        }
                    },
                    **{
                        f'question_{num}': {
                            QUESTION_INPUT_ACTION_ID.format(num): {
                                'value': 'Test?'
                            }
                        } for num in range(1, 11)
                    },
                }
            }
        }
    }
    token = action_metadata.set(ActionMetadata(**metadata))
    yield metadata
    action_metadata.reset(token)
