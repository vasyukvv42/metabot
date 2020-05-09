from fastapi import BackgroundTasks, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from fastapi_metabot.models import MetabotPayload
from fastapi_metabot.utils import current_module, slack_metadata

router = APIRouter()


@router.post('/commands/{command_name}')
async def execute_command(
        command_name: str,
        payload: MetabotPayload,
        background_tasks: BackgroundTasks,
) -> None:
    module = current_module.get()
    if module is None:
        raise HTTPException(500)

    slack_metadata.set(payload.metadata)

    background_tasks.add_task(
        module.execute_command,
        command_name,
        jsonable_encoder(payload.arguments),
    )
