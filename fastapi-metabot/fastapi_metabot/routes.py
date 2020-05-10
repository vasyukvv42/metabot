from fastapi import BackgroundTasks, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from fastapi_metabot.models import CommandPayload, ActionPayload
from fastapi_metabot.utils import (
    current_module,
    command_metadata,
    action_metadata,
)

router = APIRouter()


@router.post('/commands/{command_name}')
async def execute_command(
        command_name: str,
        payload: CommandPayload,
        background_tasks: BackgroundTasks,
) -> None:
    module = current_module.get()
    if module is None:
        raise HTTPException(500)

    command_metadata.set(payload.metadata)

    background_tasks.add_task(
        module.execute_command,
        command_name,
        jsonable_encoder(payload.arguments),
    )


@router.post('/actions/{action_id}')
async def execute_action(
        action_id: str,
        payload: ActionPayload,
        background_tasks: BackgroundTasks,
) -> None:
    module = current_module.get()
    if module is None:
        raise HTTPException(500)

    action_metadata.set(payload.metadata)
    background_tasks.add_task(module.execute_action, action_id)
