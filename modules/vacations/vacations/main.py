from fastapi import FastAPI

from fastapi_metabot.module import Module
from vacations.config import MODULE_URL, METABOT_URL

app = FastAPI()

module = Module(
    name='vacations',
    description='Manage vacations, days off & other leaves',
    module_url=MODULE_URL,
    metabot_url=METABOT_URL,
)


@module.command('test')
async def test() -> None:
    pass


module.install(app)
