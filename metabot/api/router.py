from fastapi import APIRouter

from metabot.api.routes import modules

router = APIRouter()

router.include_router(modules.router, prefix='/modules')
