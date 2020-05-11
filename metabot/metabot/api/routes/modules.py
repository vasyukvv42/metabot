from typing import Dict

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from metabot.lib.storage import Storage, get_storage
from metabot.models.module import SAMPLE_MODULE, Module

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
async def get_modules(
        storage: Storage = Depends(get_storage),
) -> GetModulesResponse:
    modules = await storage.get_all_modules()
    return GetModulesResponse(modules=modules)


@router.get('/{module_name}', response_model=Module)
async def get_module_by_name(
        module_name: str,
        storage: Storage = Depends(get_storage),
) -> Module:
    module = await storage.get_module(module_name)

    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")

    return module


@router.post('/', response_model=Module)
async def register_module(
        module: Module,
        storage: Storage = Depends(get_storage),
) -> Module:
    await storage.add_or_replace_module(module)
    return module
