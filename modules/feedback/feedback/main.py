from fastapi import FastAPI

from fastapi_metabot.module import Module
from feedback.config import MODULE_URL, METABOT_URL, MAX_QUESTIONS
from feedback.event_handlers import start_app_handler, stop_app_handler
from feedback.utils import open_creation_view, send_ephemeral

app = FastAPI()
app.add_event_handler('startup', start_app_handler(app))
app.add_event_handler('shutdown', stop_app_handler(app))

module = Module(
    name='feedback',
    description=':ledger: Create questionnaires and collect feedback',
    module_url=MODULE_URL,
    metabot_url=METABOT_URL,
)


@module.command(
    'create',
    description='Create a questionnaire & send it out to others.\n'
                'Opens a dialog with a form to create the questions',
    arg_descriptions={
        'num_of_questions': f'Number of questions you want to ask '
                            f'(max: {MAX_QUESTIONS})'
    }
)
async def create(num_of_questions: int = 1) -> None:
    if not 1 <= num_of_questions <= MAX_QUESTIONS:
        return await send_ephemeral(
            module.metabot_client,
            f'Number of questions must be between 1 and {MAX_QUESTIONS}'
        )

    await open_creation_view(module.metabot_client, num_of_questions)


module.install(app)
