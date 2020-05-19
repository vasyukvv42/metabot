import asyncio
from datetime import date
from typing import Dict, List

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorClient  # noqa

from fastapi_metabot.client import ApiClient, AsyncApis
from fastapi_metabot.client.api.metabot_api import AsyncMetabotApi
from fastapi_metabot.client.models import SlackRequest
from vacations.config import (
    METABOT_URL,
    MONGODB_URI,
    HISTORY_COLLECTION,
    ANNOUNCE_CHANNEL
)
from vacations.db import get_active_leaves


async def announce(
        api: AsyncMetabotApi,
        history: AsyncIOMotorCollection,
) -> None:
    leaves = await get_active_leaves(history, date.today())
    print(leaves)  # noqa T001
    if leaves:
        blocks = build_announce_message(leaves)
        await api.request_api_slack_post(
            SlackRequest(
                method='chat_postMessage',
                payload={
                    'channel': ANNOUNCE_CHANNEL,
                    'blocks': blocks,
                    'text': blocks[0]['text']['text']
                }
            )
        )


def build_announce_message(leaves: List[Dict]) -> List[Dict]:
    blocks: List[Dict] = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': ':wave: Hello! These people will be absent today for '
                        'various reasons :palm_tree: :mask: :relaxed::'
            }
        },
        {
            'type': 'divider'
        }
    ]
    blocks += [{
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': f'• <@{leave["user_id"]}> is on a leave '
                    f'*({leave["leave_type"]})* until *'
                    f'{leave["date_to"].date().isoformat()}*'
        }
    } for leave in leaves]
    return blocks


async def main() -> None:
    client = ApiClient(METABOT_URL)
    api = AsyncApis(client).metabot_api

    motor = AsyncIOMotorClient(MONGODB_URI)
    db = motor.get_default_database()
    history = db[HISTORY_COLLECTION]

    await announce(api, history)


if __name__ == '__main__':
    asyncio.run(main())
