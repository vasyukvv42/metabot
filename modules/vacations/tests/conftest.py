from datetime import datetime
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
environ['ADMIN_CHANNEL'] = 'ADMIN'
environ['LEAVE_TYPES'] = 'test:0.1'

from vacations.config import (
    VACATION_TYPE_ACTION_ID,
    DATEPICKER_START_ACTION_ID,
    DATEPICKER_END_ACTION_ID,
    REASON_INPUT_ACTION_ID
)


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
                    'type': {
                        VACATION_TYPE_ACTION_ID: {
                            'selected_option': {
                                'value': 'test'
                            }
                        }
                    },
                    'start': {
                        DATEPICKER_START_ACTION_ID: {
                            'selected_date': '2020-10-31'
                        }
                    },
                    'end': {
                        DATEPICKER_END_ACTION_ID: {
                            'selected_date': '2020-10-31'
                        }
                    },
                    'reason': {
                        REASON_INPUT_ACTION_ID: {
                            'value': 'asdasd'
                        }
                    }
                }
            }
        }
    }
    token = action_metadata.set(ActionMetadata(**metadata))
    yield metadata
    action_metadata.reset(token)


@pytest.fixture
def module() -> Module:
    from vacations.main import module
    return module


@pytest.fixture
def test_request() -> Dict:
    return {
        '_id': '123asd',
        'leave_type': 'test',
        'duration': 1,
        'user_id': 'U123',
        'date_from': datetime(2020, 10, 31),
        'date_to': datetime(2020, 10, 31),
        'reason': 'asd',
        'approval_status': 'unapproved',
    }
