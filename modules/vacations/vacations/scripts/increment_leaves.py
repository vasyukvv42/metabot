import asyncio
from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection  # noqa

from fastapi_metabot.client import ApiClient, AsyncApis
from fastapi_metabot.client.api.metabot_api import AsyncMetabotApi
from fastapi_metabot.client.models import SlackRequest
from vacations.config import (
    METABOT_URL,
    MONGODB_URI,
    USERS_COLLECTION
)
from vacations.db import increase_days_by_config


async def list_users(api: AsyncMetabotApi) -> AsyncGenerator:
    payload = {'limit': 100}
    while True:
        result = await api.request_api_slack_post(
            SlackRequest(
                method='users_list',
                payload=payload
            )
        )
        yield result.data.get('members', [])

        cursor = result.data.get('response_metadata', {}).get('next_cursor')
        if not cursor:
            return
        payload['cursor'] = cursor


async def main() -> None:
    client = ApiClient(METABOT_URL)
    api = AsyncApis(client).metabot_api

    motor = AsyncIOMotorClient(MONGODB_URI)
    db = motor.get_default_database()

    users = db[USERS_COLLECTION]

    async for members in list_users(api):
        users_list = [member['id'] for member in members]
        print(f'Adding more leave days to users: {users_list}')  # noqa T001
        await increase_days_by_config(users, users_list)


if __name__ == '__main__':
    asyncio.run(main())
