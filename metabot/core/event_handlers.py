import asyncio
import logging
from typing import Callable

import aioredis
from aiohttp import ClientSession
from fastapi import FastAPI
from slack import WebClient
from slackers.hooks import commands

from metabot.core.config import SLACK_API_TOKEN, REDIS_URL
from metabot.lib.dispatcher import CommandDispatcher
from metabot.lib.storage import Storage

log = logging.getLogger(__name__)


def start_app_handler(app: FastAPI) -> Callable:
    async def startup() -> None:
        app.state.session = ClientSession()
        app.state.slack = WebClient(
            token=SLACK_API_TOKEN,
            run_async=True,
            session=app.state.session,
        )
        app.state.redis = await aioredis.create_redis_pool(REDIS_URL)
        app.state.storage = Storage(app.state.redis)

        app.state.dispatcher = CommandDispatcher(app)
        commands.on('meta', app.state.dispatcher.dispatch)

    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    async def shutdown() -> None:
        await app.state.session.close()
        # Wait 250 ms for the underlying SSL connections to close
        await asyncio.sleep(0.250)

    return shutdown
