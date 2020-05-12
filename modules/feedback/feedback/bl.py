import asyncio
import logging
from typing import Dict, Tuple, List, Optional, FrozenSet

from motor.motor_asyncio import AsyncIOMotorCollection  # noqa

from fastapi_metabot.client import ApiClient, AsyncApis
from fastapi_metabot.client.models import SlackRequest
from fastapi_metabot.utils import (
    command_metadata,
    get_current_user_id,
    get_current_channel_id,
    action_metadata
)
from feedback.builders import (
    build_creation_view,
    build_control_message,
    build_answer_message, build_answer_view, build_submitted_feedback_message
)
from feedback.config import (
    QUESTION_INPUT_ACTION_ID,
    RECIPIENTS_SELECT_ACTION_ID,
    TITLE_INPUT_ACTION_ID, MAX_QUESTIONS, ANSWER_INPUT_ACTION_ID
)
from feedback.db import (
    save_questionnaire,
    update_questionnaire_ts,
    get_questionnaire_by_id, update_questionnaire_answers
)

log = logging.getLogger(__name__)


async def send_ephemeral(
        metabot_client: ApiClient,
        text: str
) -> None:
    user = await get_current_user_id()
    log.info(f'Sending ephemeral to user {user}: {text}')
    api = AsyncApis(metabot_client).metabot_api
    await api.request_api_slack_post(
        SlackRequest(
            method='chat_postEphemeral',
            payload={
                'text': text,
                'user': user,
                'channel': await get_current_channel_id()
            }
        )
    )


async def open_creation_view(
        metabot_client: ApiClient,
        num_of_questions: int
) -> None:
    metadata = command_metadata.get()
    assert metadata is not None, 'Must be called from command context'

    api = AsyncApis(metabot_client).metabot_api
    await api.request_api_slack_post(
        SlackRequest(
            method='views_open',
            payload={
                'trigger_id': metadata.trigger_id,
                'view': build_creation_view(num_of_questions)
            }
        )
    )


async def open_answer_view(
        collection: AsyncIOMotorCollection,
        metabot_client: ApiClient,
        q_id: str
) -> None:
    metadata = action_metadata.get()
    assert metadata and metadata.actions, 'Must be called from action context'

    questionnaire = await get_questionnaire_by_id(collection, q_id)
    assert questionnaire is not None, "Couldn't find questionnaire by _id"

    user = await get_current_user_id()
    if user not in _get_not_answered_recipients(questionnaire):
        return await send_ephemeral(
            metabot_client,
            'You have already sent your feedback on this questionnaire.'
        )

    api = AsyncApis(metabot_client).metabot_api
    await api.request_api_slack_post(
        SlackRequest(
            method='views_open',
            payload={
                'trigger_id': metadata.trigger_id,
                'view': build_answer_view(
                    questionnaire['title'],
                    questionnaire['questions'],
                    q_id
                )
            }
        )
    )


async def parse_creation_view() -> Tuple[str, List[str], List[str]]:
    metadata = action_metadata.get()
    assert metadata and metadata.view, 'Must be called from view context'

    values = metadata.view['state']['values']
    title = values['title'][TITLE_INPUT_ACTION_ID]['value']
    recipients = (
        values['recipients'][RECIPIENTS_SELECT_ACTION_ID]['selected_users']
    )
    questions = []
    for num in range(1, MAX_QUESTIONS + 1):
        block = values.get(f'question_{num}')
        if block is None:
            break
        question = block[QUESTION_INPUT_ACTION_ID.format(num)].get('value')
        if question is not None:
            questions.append(question)

    return title, recipients, questions


async def parse_answer_view() -> Tuple[str, List[str]]:
    metadata = action_metadata.get()
    assert metadata and metadata.view, 'Must be called from view context'

    q_id = metadata.view['private_metadata']
    answers = []
    for num in range(1, MAX_QUESTIONS + 1):
        block = metadata.view['state']['values'].get(f'answer_{num}')
        if block is None:
            break
        answers.append(block[ANSWER_INPUT_ACTION_ID.format(num)].get('value'))

    return q_id, answers


async def _send_control_message(
        metabot_client: ApiClient,
        title: str,
        recipients: List[str],
        questions: List[str],
        questionnaire_id: str
) -> Optional[str]:
    blocks = build_control_message(
        questionnaire_id,
        questions,
        recipients,
        title
    )
    return await _send_message(
        metabot_client,
        blocks[0]['text'],
        blocks
    )


async def _send_message(
        metabot_client: ApiClient,
        text: str,
        blocks: Optional[List[Dict]] = None,
        channel_id: Optional[str] = None,
        thread_ts: Optional[str] = None,
        reply_broadcast: Optional[bool] = None
) -> Optional[str]:
    if channel_id is None:
        channel_id = await get_current_user_id()

    log.info(f'Sending message to channel {channel_id}: {text}')
    api = AsyncApis(metabot_client).metabot_api
    resp = await api.request_api_slack_post(
        SlackRequest(
            method='chat_postMessage',
            payload={
                'text': text,
                'channel': channel_id,
                'blocks': blocks,
                'thread_ts': thread_ts,
                'reply_broadcast': reply_broadcast
            }
        )
    )
    return resp.data.get('ts')


async def _send_answer_message(
        metabot_client: ApiClient,
        recipient: str,
        author: str,
        title: str,
        q_id: str
) -> None:
    blocks = build_answer_message(author, q_id, title)
    await _send_message(
        metabot_client,
        blocks[0]['text']['text'],
        blocks,
        recipient
    )


async def notify_recipients(
        collection: AsyncIOMotorCollection,
        metabot_client: ApiClient,
        q_id: str
) -> None:
    questionnaire = await get_questionnaire_by_id(collection, q_id)
    assert questionnaire is not None, "Couldn't find questionnaire by _id"

    recipients = _get_not_answered_recipients(questionnaire)
    if not recipients:
        return await send_ephemeral(
            metabot_client,
            'There is no one left to notify :)'
        )

    author = questionnaire['user_id']
    title = questionnaire['title']
    futures = [
        _send_answer_message(metabot_client, recipient, author, title, q_id)
        for recipient in recipients
    ]
    await asyncio.gather(*futures)


def _get_not_answered_recipients(questionnaire: Dict) -> FrozenSet[str]:
    return (
        frozenset(questionnaire.get('recipients', []))
        - frozenset(questionnaire.get('answers', {}).keys())
    )


async def create_questionnaire(
        collection: AsyncIOMotorCollection,
        metabot_client: ApiClient,
        title: str,
        recipients: List[str],
        questions: List[str]
) -> None:
    user = await get_current_user_id()
    assert user is not None, 'Must be called from any Slack context'

    q_id = await save_questionnaire(
        collection, user, title, recipients, questions
    )
    ts = await _send_control_message(
        metabot_client,
        title,
        recipients,
        questions,
        q_id
    )
    await update_questionnaire_ts(collection, q_id, ts)
    await notify_recipients(collection, metabot_client, q_id)


async def get_q_id_from_button() -> str:
    metadata = action_metadata.get()
    assert metadata and metadata.actions, 'Must be called from action context'
    return metadata.actions[0]['value']


async def submit_answers(
        collection: AsyncIOMotorCollection,
        metabot_client: ApiClient,
        q_id: str,
        answers: List[str]
) -> None:
    user = await get_current_user_id()
    assert user is not None, 'Must be called from any Slack context'

    questionnaire = await get_questionnaire_by_id(collection, q_id)
    assert questionnaire is not None, "Couldn't find questionnaire by _id"
    assert user in _get_not_answered_recipients(questionnaire)

    after = await update_questionnaire_answers(collection, q_id, user, answers)

    await _send_message(
        metabot_client,
        f'Your feedback on *"{after["title"]}"* has been submitted!',
        channel_id=user,

    )

    blocks = build_submitted_feedback_message(user, after['questions'], answers)
    await _send_message(
        metabot_client,
        blocks[0]['text']['text'],
        blocks,
        after['user_id'],
        after['ts']
    )

    if not _get_not_answered_recipients(after):
        await _send_message(
            metabot_client,
            'All recipients have sent their answers! :tada:',
            channel_id=after['user_id'],
            thread_ts=after['ts'],
            reply_broadcast=True
        )
