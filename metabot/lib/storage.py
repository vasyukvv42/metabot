import json
import logging
from typing import Dict, Optional, List, AsyncIterator

from aioredis import Redis
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request

from metabot.core.config import MODULE_EXPIRATION_SECONDS
from metabot.models.module import Module

log = logging.getLogger(__name__)


async def get_storage(request: Request) -> 'Storage':
    return request.app.state.storage


class Storage:
    redis: Redis

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    @staticmethod
    def _encode_module(module: Module) -> str:
        return json.dumps(jsonable_encoder(module))

    @staticmethod
    def _decode_module(raw_module: str) -> Module:
        return Module.parse_raw(raw_module)

    async def add_or_replace_module(self, module: Module) -> None:
        tr = self.redis.multi_exec()
        tr.set(
            f'module:{module.name}',
            self._encode_module(module),
            expire=MODULE_EXPIRATION_SECONDS,
        )
        for action in module.actions:
            tr.set(
                f'action:{action}',
                module.name,
                expire=MODULE_EXPIRATION_SECONDS,
            )
        await tr.execute()

    async def get_module(self, module_name: str) -> Optional[Module]:
        raw_module = await self.redis.get(f'module:{module_name}')
        if raw_module is None:
            return None
        return self._decode_module(raw_module)

    async def get_module_by_action(self, action: str) -> Optional[Module]:
        module_name = await self.redis.get(f'action:{action}')
        if module_name is None:
            return None
        return await self.get_module(module_name.decode('utf-8'))

    async def _module_keys(self) -> AsyncIterator[str]:
        async for key in self.redis.iscan(match='module:*'):
            yield key.decode('utf-8')

    async def get_all_modules(self) -> Dict[str, Module]:
        results = {}
        async for key in self._module_keys():
            raw_module = await self.redis.get(key)
            if raw_module:
                module = self._decode_module(raw_module)
                results[module.name] = module
        return results

    async def get_module_names(self) -> List[str]:
        return [key.split(':')[-1] async for key in self._module_keys()]
