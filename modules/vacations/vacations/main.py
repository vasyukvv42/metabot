from datetime import date
from decimal import Decimal
from re import search

from fastapi import FastAPI

from fastapi_metabot.module import Module
from vacations.config import (
    MODULE_URL,
    METABOT_URL,
    REQUEST_VIEW_ID,
    APPROVE_BUTTON_ACTION_ID,
    DENY_BUTTON_ACTION_ID,
    LEAVE_TYPES
)
from vacations.event_handlers import start_app_handler, stop_app_handler
from vacations.bl import (
    send_ephemeral,
    open_request_view,
    parse_request_view,
    get_request_id_from_button,
    is_admin_channel,
    send_history,
    create_request,
    add_days,
    approve_request,
    deny_request
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


class UserId(str):
    pass


@module.converter(UserId)
async def convert_user_id(user_id: str) -> UserId:
    user_id_search = search(r'<@(\w+)\|(\w+)>', user_id)

    if user_id_search:
        return UserId(user_id_search.group(1))
    else:
        await send_ephemeral(f'Invalid user mention: `{user_id}`')
        raise ValueError('Invalid UserId')


@module.converter(date)
async def convert_date(iso_date: str) -> date:
    try:
        return date.fromisoformat(iso_date)
    except ValueError as e:
        await send_ephemeral(f'Invalid date format: `{iso_date}`')
        raise e


@module.converter(Decimal)
async def convert_decimal(number: str) -> Decimal:
    try:
        return Decimal(number)
    except ArithmeticError as e:
        await send_ephemeral(f'Invalid number: `{number}`')
        raise e


@module.command(
    'request',
    description='Request a vacation, day off or another leave.\n'
                'If no arguments are provided, opens a dialog with a form to '
                'fill out your request.',
    arg_descriptions={
        'leave_type': f'Type of your leave '
                      f'(one of `{"` `".join(LEAVE_TYPES)}`)',
        'date_from': 'The day you want to start your leave (e.g. `2020-10-29`)',
        'date_to': 'End date of your leave (e.g. `2020-10-31`)',
        'reason': 'Reason for your leave '
                  '(e.g. `"Going on a trip with my family"`)'
    }
)
async def request(
        leave_type: str = None,
        date_from: date = None,
        date_to: date = None,
        reason: str = '',
) -> None:
    if leave_type is None:
        return await open_request_view(app.state.users)

    await create_request(
        app.state.history,
        app.state.users,
        leave_type,
        date_from,
        date_to,
        reason
    )


@module.command(
    'approve',
    description='Approve a vacation request.\n'
                'Available only in the admin channel.',
    arg_descriptions={
        'request_id': 'Id of the request to be approved '
                      '(e.g. `5eb95d610ec29ce040c8c144`)'
    }
)
async def approve(request_id: str) -> None:
    if not await is_admin_channel():
        return await send_ephemeral(
            'This command is available only in the admin channel.'
        )

    await approve_request(
        app.state.history,
        app.state.users,
        request_id,
    )


@module.command(
    'deny',
    description='Deny a vacation request.\n'
                'Available only in the admin channel.',
    arg_descriptions={
        'request_id': 'Id of the request to be denied '
                      '(e.g. `5eb95d610ec29ce040c8c144`)'
    }
)
async def deny(request_id: str) -> None:
    if not await is_admin_channel():
        return await send_ephemeral(
            'This command is available only in the admin channel.'
        )

    await deny_request(app.state.history, request_id)


@module.command(
    'stats',
    description='View available leave days and leaves history of a user '
                '(or yourself if no user is provided).\n'
                'Stats of users other than you are only available '
                'in the admin channel.',
    arg_descriptions={
        'user': 'Mention of a user (e.g. `<@metabot>`)'
    }
)
async def stats(user: UserId = None) -> None:
    await send_history(app.state.history, app.state.users, user)


@module.command(
    'add',
    description='Add more leave days to a user (or all users). '
                'Only available in the admin channel.',
    arg_descriptions={
        'leave_type': f'Type of leave you want to add days for '
                      f'(one of `{"` `".join(LEAVE_TYPES)}`)',
        'days': 'Number of days (e.g. `5`)',
        'user': 'Mention of a user (e.g. `<@metabot>`)'
    }
)
async def add(leave_type: str, days: Decimal, user: UserId = None) -> None:
    if not await is_admin_channel():
        return await send_ephemeral(
            'This command is available only in the admin channel.'
        )

    await add_days(app.state.users, leave_type, days, user)


@module.view(REQUEST_VIEW_ID)
async def request_view() -> None:
    leave_type, date_from, date_to, reason = await parse_request_view()
    await create_request(
        app.state.history,
        app.state.users,
        leave_type,
        date_from,
        date_to,
        reason
    )


@module.action(APPROVE_BUTTON_ACTION_ID)
async def approve_button_action() -> None:
    if not await is_admin_channel():
        return await send_ephemeral(
            'This command is available only in the admin channel.'
        )

    request_id = await get_request_id_from_button()
    await approve_request(
        app.state.history,
        app.state.users,
        request_id,
    )


@module.action(DENY_BUTTON_ACTION_ID)
async def deny_button_action() -> None:
    if not await is_admin_channel():
        return await send_ephemeral(
            'This command is available only in the admin channel.'
        )

    request_id = await get_request_id_from_button()
    await deny_request(app.state.history, request_id)


module.install(app)
