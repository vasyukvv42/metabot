from fastapi import FastAPI
from slackers.server import router as slackers_router

from metabot.core.config import APP_TITLE, API_PREFIX, SLACKERS_PREFIX
from metabot.core.event_handlers import start_app_handler, stop_app_handler
from metabot.api.router import router as api_router

app = FastAPI(title=APP_TITLE)

app.add_event_handler('startup', start_app_handler(app))
app.add_event_handler('shutdown', stop_app_handler(app))

app.include_router(slackers_router, prefix=SLACKERS_PREFIX)
app.include_router(api_router, prefix=API_PREFIX)
