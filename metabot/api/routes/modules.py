from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from metabot.models.module import SAMPLE_MODULE, Module
from metabot.lib.storage import (
    get_all_modules,
    get_module,
    add_or_replace_module,
)

router = APIRouter()


class GetModulesResponse(BaseModel):
    modules: Dict[str, Module]

    class Config:
        schema_extra = {
            'example': {
                SAMPLE_MODULE['name']: SAMPLE_MODULE
            }
        }


@router.get('/', response_model=GetModulesResponse)
async def get_modules() -> GetModulesResponse:
    return GetModulesResponse(modules=get_all_modules())


@router.get('/{module_name}', response_model=Module)
async def get_module_by_name(module_name: str) -> Module:
    module = get_module(module_name)

    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")

    return module


@router.post('/', response_model=Module)
async def register_module(module: Module) -> Module:
    add_or_replace_module(module)
    return module
