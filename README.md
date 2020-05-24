# Metabot for Slack
![metabot server](https://github.com/vasyukvv42/metabot/workflows/metabot%20server/badge.svg)
![fastapi_metabot package](https://github.com/vasyukvv42/metabot/workflows/fastapi_metabot%20package/badge.svg)

![modules/vacations](https://github.com/vasyukvv42/metabot/workflows/modules/vacations/badge.svg)
![modules/help](https://github.com/vasyukvv42/metabot/workflows/modules/help/badge.svg)
![modules/feedback](https://github.com/vasyukvv42/metabot/workflows/modules/feedback/badge.svg)

Metabot is a Slack bot written using FastAPI which allows you to dynamically 
add new functionality (commands, interactive components & modals) via modules.

## Module example
**Step 1:** `pip install fastapi-metabot`

**Step 2:** create `example.py`
```python
from fastapi import FastAPI
from fastapi_metabot.module import Module
from fastapi_metabot.utils import (
    command_metadata, 
    action_metadata, 
    async_slack_request
)

app = FastAPI()

module = Module(
    name='example',
    description='Example module',
    module_url='http://example:8000',  # URL of this module
    metabot_url='http://metabot:8000'  # URL of the Metabot server
)


# /meta example test "param" "optional"
# command arguments are based on your function parameters
@module.command('test')  
async def test(param: int, optional: str = 'default') -> None:
    # argument values are casted from str according to the annotation
    # use @module.converter(Type) to provide custom cast functions
    print(type(param))  # <class 'int'>

    # you can access any Slack API method via the client
    await async_slack_request(
        method='chat_postMessage',
        payload={
            'text': 'Hello, World!',
            'channel': '#general'
        }
    )

    # Slack command/action payloads are stored inside contextvars
    payload = command_metadata.get()
    print(payload.user_name)  # current user's name


# note that action and view ids must be unique across ALL modules
@module.action('action_id')
async def action() -> None:
    # this is called when someone triggers an interactive component
    payload = action_metadata.get()
    print(payload.actions)


@module.view('callback_id')
async def view() -> None:
    # this is called when someone submits a modal
    payload = action_metadata.get()
    print(payload.view)


# this creates a few routes for Metabot and starts the heartbeat
module.install(app)
```

**Step 3:** `uvicorn example:app --reload`

## How it works
![architecture](https://user-images.githubusercontent.com/22105178/82678326-157d3580-9c52-11ea-896a-c678accf229d.png)

Metabot and its modules communicate via HTTP APIs:

* Metabot listens to Slack `/meta` slash command and actions (e.g. buttons, 
modals) which it then dispatches to modules 
(`/api/commands` and `/api/actions`) as needed
* Metabot exposes endpoints to get info about other modules 
(`/api/modules`) and access Slack API (`/api/slack`)
* Each module sends a POST request every few seconds (heartbeat) to 
`/api/modules` with info about the module itself, available commands, 
actions and views
* Modules are removed from Metabot automatically if they have not sent 
a heartbeat for `MODULE_EXPIRATION_SECONDS` (30 by default)

## Modules
* `help` – display help about other modules
* `vacations` – manage vacations and other leaves in your company
* `feedback` – create questionnaires and send them out to collect feedback

For more details, use the `/meta help me` command. 
