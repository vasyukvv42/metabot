from asyncio import get_event_loop
from typing import TYPE_CHECKING, Awaitable

from fastapi.encoders import jsonable_encoder

from fastapi_metabot.client import models as m

if TYPE_CHECKING:
    from fastapi_metabot.client.api_client import ApiClient


class _MetabotApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_get_module_by_name_api_modules_module_name_get(self, module_name: str) -> Awaitable[m.Module]:
        path_params = {"module_name": str(module_name)}

        return self.api_client.request(
            type_=m.Module, method="GET", url="/api/modules/{module_name}", path_params=path_params,
        )

    def _build_for_get_modules_api_modules_get(self,) -> Awaitable[m.GetModulesResponse]:
        return self.api_client.request(type_=m.GetModulesResponse, method="GET", url="/api/modules/",)

    def _build_for_register_module_api_modules_post(self, module: m.Module) -> Awaitable[m.Module]:
        body = jsonable_encoder(module)

        return self.api_client.request(type_=m.Module, method="POST", url="/api/modules/", json=body)

    def _build_for_request_api_slack_post(self, slack_request: m.SlackRequest) -> Awaitable[m.SlackResponse]:
        body = jsonable_encoder(slack_request)

        return self.api_client.request(type_=m.SlackResponse, method="POST", url="/api/slack/", json=body)


class AsyncMetabotApi(_MetabotApi):
    async def get_module_by_name_api_modules_module_name_get(self, module_name: str) -> m.Module:
        return await self._build_for_get_module_by_name_api_modules_module_name_get(module_name=module_name)

    async def get_modules_api_modules_get(self,) -> m.GetModulesResponse:
        return await self._build_for_get_modules_api_modules_get()

    async def register_module_api_modules_post(self, module: m.Module) -> m.Module:
        return await self._build_for_register_module_api_modules_post(module=module)

    async def request_api_slack_post(self, slack_request: m.SlackRequest) -> m.SlackResponse:
        return await self._build_for_request_api_slack_post(slack_request=slack_request)


class SyncMetabotApi(_MetabotApi):
    def get_module_by_name_api_modules_module_name_get(self, module_name: str) -> m.Module:
        coroutine = self._build_for_get_module_by_name_api_modules_module_name_get(module_name=module_name)
        return get_event_loop().run_until_complete(coroutine)

    def get_modules_api_modules_get(self,) -> m.GetModulesResponse:
        coroutine = self._build_for_get_modules_api_modules_get()
        return get_event_loop().run_until_complete(coroutine)

    def register_module_api_modules_post(self, module: m.Module) -> m.Module:
        coroutine = self._build_for_register_module_api_modules_post(module=module)
        return get_event_loop().run_until_complete(coroutine)

    def request_api_slack_post(self, slack_request: m.SlackRequest) -> m.SlackResponse:
        coroutine = self._build_for_request_api_slack_post(slack_request=slack_request)
        return get_event_loop().run_until_complete(coroutine)
