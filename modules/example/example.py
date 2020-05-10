from datetime import datetime

from fastapi import FastAPI

from fastapi_metabot.client import AsyncApis
from fastapi_metabot.client.models import Message
from fastapi_metabot.module import Module

app = FastAPI()

module = Module(
    name='example',
    description='Example module',
    module_url='http://example:8000',
    metabot_url='http://metabot:8000',
)

module.converter(datetime, converter=datetime.fromisoformat)


@module.command('test', description='Test command')
async def test(test_argument: str, kek: datetime) -> None:
    api = AsyncApis(module.metabot_client)
    await api.metabot_api.send_message_to_slack_api_chat_post(
        Message(
            channel_id='#memes',
            text=test_argument,
            send_ephemeral=False
        )
    )


module.install(app)
