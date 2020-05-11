from datetime import date

from fastapi import FastAPI

from fastapi_metabot.module import Module
from vacations.config import MODULE_URL, METABOT_URL
from vacations.utils import send_error

app = FastAPI()

module = Module(
    name='vacations',
    description=':palm_tree: Manage vacations, days off & other leaves',
    module_url=MODULE_URL,
    metabot_url=METABOT_URL,
)


@module.converter(date)
async def convert_date(iso_date: str) -> date:
    try:
        return date.fromisoformat(iso_date)
    except ValueError as e:
        await send_error(
            module.metabot_client,
            f'Invalid date format: `{iso_date}`'
        )
        raise e


@module.command(
    'request',
    description='Request a vacation, day off or another leave.\n'
                'If no arguments are provided, opens a dialog with a form to '
                'fill out your request.',
    arg_descriptions={
        'date_from': 'The day you want to start your leave (e.g. `2020-10-29`)',
        'date_to': 'End date of your leave (e.g. `2020-10-31`)',
        'reason': 'Reason for your leave '
                  '(e.g. `"Going on a trip with my family"`)'
    }
)
async def request(
        date_from: date = None,
        date_to: date = None,
        reason: str = None,
) -> None:
    print(type(date_from))
    print(type(date_to))
    print(reason, flush=True)


module.install(app)
