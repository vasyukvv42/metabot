from fastapi import APIRouter

from metabot.api.routes import modules, slack

router = APIRouter()

router.include_router(modules.router, prefix='/modules')
router.include_router(slack.router, prefix='/slack')
