import pytest
from starlette.config import environ

from fastapi_metabot.module import Module

environ['HEARTBEAT_DELAY'] = '0'
environ['METABOT_URL'] = 'http://localhost'
environ['MODULE_URL'] = 'http://localhost'
environ['MONGODB_URI'] = 'mongodb://localhost:27017'


@pytest.fixture
def module() -> Module:
    from feedback.main import module
    return module
