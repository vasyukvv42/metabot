import asyncio
import logging
from typing import Dict, Tuple, List, Optional

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
    build_answer_message
)
from feedback.config import (
    QUESTION_INPUT_ACTION_ID,
    RECIPIENTS_SELECT_ACTION_ID,
    TITLE_INPUT_ACTION_ID, MAX_QUESTIONS
)
from feedback.db import (
    save_questionnaire,
    update_questionnaire_ts,
    get_questionnaire_by_id
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
    if metadata is None:
        raise ValueError('Must be called from command context')

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
                'thread_ts': thread_ts
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
    await _send_message(metabot_client, blocks[0]['text'], blocks, recipient)


async def notify_recipients(
        collection: AsyncIOMotorCollection,
        metabot_client: ApiClient,
        q_id: str
) -> None:
    questionnaire = await get_questionnaire_by_id(collection, q_id)
    assert questionnaire is not None, "Couldn't find questionnaire by _id"

    recipients = (
        frozenset(questionnaire.get('recipients', []))
        - frozenset(questionnaire.get('answers', {}).keys())
    )
    author = questionnaire['user_id']
    title = questionnaire['title']
    futures = [
        _send_answer_message(metabot_client, recipient, author, title, q_id)
        for recipient in recipients
    ]
    await asyncio.gather(*futures)


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
