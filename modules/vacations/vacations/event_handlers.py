from typing import Callable

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from vacations.config import (
    MONGODB_URI,
    HISTORY_COLLECTION
)


def start_app_handler(app: FastAPI) -> Callable:
    async def startup() -> None:
        app.state.motor = AsyncIOMotorClient(MONGODB_URI)
        db = app.state.motor.get_default_database()
        app.state.history = db[HISTORY_COLLECTION]

    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    async def shutdown() -> None:
        app.state.motor.close()

    return shutdown
