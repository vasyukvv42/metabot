from datetime import date
from re import search

from fastapi import FastAPI

from fastapi_metabot.module import Module
from vacations.config import (
    MODULE_URL,
    METABOT_URL,
    REQUEST_VIEW_ID,
    APPROVE_BUTTON_ACTION_ID,
    DENY_BUTTON_ACTION_ID
)
from vacations.event_handlers import start_app_handler, stop_app_handler
from vacations.utils import (
    send_ephemeral,
    open_request_view,
    parse_view,
    process_request,
    get_request_id_from_button,
    is_admin_channel,
    send_history,
    create_request
)

app = FastAPI()
app.add_event_handler('startup', start_app_handler(app))
app.add_event_handler('shutdown', stop_app_handler(app))

module = Module(
    name='vacations',
    description=':palm_tree: Manage vacations, days off & other leaves',
    module_url=MODULE_URL,
    metabot_url=METABOT_URL,
)

UserId = str


@module.converter(date)
async def convert_date(iso_date: str) -> date:
    try:
        return date.fromisoformat(iso_date)
    except ValueError as e:
        await send_ephemeral(
            module.metabot_client,
            f'Invalid date format: `{iso_date}`'
        )
        raise e


@module.converter(UserId)
async def convert_user_id(user_id: str) -> UserId:
    user_id_search = search(r'<@(\w+)\|(\w+)>', user_id)

    if user_id_search:
        return user_id_search.group(1)
    else:
        await send_ephemeral(
            module.metabot_client,
            f'Invalid user mention: `{user_id}`'
        )
        raise ValueError('Invalid UserId')


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
        reason: str = 'Vacation',
) -> None:
    if date_from is None:
        return await open_request_view(module.metabot_client)

    await create_request(
        module.metabot_client,
        app.state.history,
        date_from,
        date_to,
        reason
    )


@module.command(
    'approve',
    description=f'Approve a vacation request.\n'
                f'Available only in the admin channel.',
    arg_descriptions={
        'request_id': 'Id of the request to be approved '
                      '(e.g. `5eb95d610ec29ce040c8c144`)'
    }
)
async def approve(request_id: str) -> None:
    if not await is_admin_channel():
        return await send_ephemeral(
            module.metabot_client,
            'This command is available only in the admin channel.'
        )

    await process_request(
        app.state.history,
        module.metabot_client,
        request_id,
        'approved',
    )


@module.command(
    'deny',
    description=f'Deny a vacation request.\n'
                f'Available only in the admin channel.',
    arg_descriptions={
        'request_id': 'Id of the request to be denied '
                      '(e.g. `5eb95d610ec29ce040c8c144`)'
    }
)
async def deny(request_id: str) -> None:
    if not await is_admin_channel():
        return await send_ephemeral(
            module.metabot_client,
            'This command is available only in the admin channel.'
        )

    await process_request(
        app.state.history,
        module.metabot_client,
        request_id,
        'denied',
    )


@module.command(
    'history',
    description='View leaves history of a user '
                '(or yourself if no user is provided).\n'
                'History of users other than you is only available '
                'in the admin channel.',
    arg_descriptions={
        'user': 'Mention of a user (e.g. `<@meta_bot>`)'
    }
)
async def history(user: UserId = None) -> None:
    await send_history(app.state.history, module.metabot_client, user)


@module.view(REQUEST_VIEW_ID)
async def request_view() -> None:
    date_from, date_to, reason = await parse_view()
    await create_request(
        module.metabot_client,
        app.state.history,
        date_from,
        date_to,
        reason
    )


@module.action(APPROVE_BUTTON_ACTION_ID)
async def approve_button_action() -> None:
    request_id = await get_request_id_from_button()
    await process_request(
        app.state.history,
        module.metabot_client,
        request_id,
        'approved'
    )


@module.action(DENY_BUTTON_ACTION_ID)
async def deny_button_action() -> None:
    request_id = await get_request_id_from_button()
    await process_request(
        app.state.history,
        module.metabot_client,
        request_id,
        'denied',
    )


module.install(app)
