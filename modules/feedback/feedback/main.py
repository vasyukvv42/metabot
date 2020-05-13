from fastapi import FastAPI

from fastapi_metabot.module import Module
from feedback.config import (
    MODULE_URL,
    METABOT_URL,
    MAX_QUESTIONS,
    CREATION_VIEW_ID,
    NOTIFY_ACTION_ID,
    ANSWER_VIEW_ID,
    ANSWER_ACTION_ID
)
from feedback.event_handlers import start_app_handler, stop_app_handler
from feedback.bl import (
    open_creation_view,
    send_ephemeral,
    parse_creation_view,
    create_questionnaire,
    get_q_id_from_button,
    notify_recipients,
    open_answer_view,
    parse_answer_view,
    submit_answers
)

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
            f'Number of questions must be between 1 and {MAX_QUESTIONS}'
        )

    await open_creation_view(num_of_questions)


@module.view(CREATION_VIEW_ID)
async def creation_view() -> None:
    title, recipients, questions = await parse_creation_view()
    await create_questionnaire(
        app.state.feedback,
        title,
        recipients,
        questions
    )


@module.view(ANSWER_VIEW_ID)
async def answer_view() -> None:
    q_id, answers = await parse_answer_view()
    await submit_answers(
        app.state.feedback,
        q_id,
        answers
    )


@module.action(NOTIFY_ACTION_ID)
async def notify() -> None:
    q_id = await get_q_id_from_button()
    await notify_recipients(app.state.feedback, q_id)


@module.action(ANSWER_ACTION_ID)
async def answer() -> None:
    q_id = await get_q_id_from_button()
    await open_answer_view(app.state.feedback, q_id)


module.install(app)
