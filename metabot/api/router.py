from fastapi import APIRouter

from metabot.api.routes import modules, chat

router = APIRouter()

router.include_router(modules.router, prefix='/modules')
router.include_router(chat.router, prefix='/chat')
