import logging
from typing import Dict

from fastapi_metabot.client import ApiClient, AsyncApis
from fastapi_metabot.client.models import SlackRequest
from fastapi_metabot.utils import (
    command_metadata,
    get_current_user_id,
    get_current_channel_id
)

log = logging.getLogger(__name__)

DIVIDER = {
    'type': 'divider'
}


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
                'view': _build_creation_view(num_of_questions)
            }
        )
    )


def _build_creation_view(num_of_questions: int) -> Dict:
    blocks = [
        {
            'type': 'input',
            'element': {
                'type': 'plain_text_input'
            },
            'label': {
                'type': 'plain_text',
                'text': 'Title',
                'emoji': True
            }
        },
        {
            'type': 'input',
            'element': {
                'type': 'multi_users_select',
                'placeholder': {
                    'type': 'plain_text',
                    'text': 'Select users',
                    'emoji': True
                }
            },
            'label': {
                'type': 'plain_text',
                'text': 'Recipients',
                'emoji': True
            }
        },
        DIVIDER,
        _build_question_input()
    ]
    for question_number in range(2, num_of_questions + 1):
        blocks.append(_build_question_input(question_number, True))
    return {
        'type': 'modal',
        'title': {
            'type': 'plain_text',
            'text': 'Create a questionnaire',
            'emoji': True
        },
        'submit': {
            'type': 'plain_text',
            'text': 'Submit',
            'emoji': True
        },
        'close': {
            'type': 'plain_text',
            'text': 'Cancel',
            'emoji': True
        },
        'blocks': blocks
    }


def _build_question_input(num: int = 1, optional: bool = False) -> Dict:
    return {
        'type': 'input',
        'optional': optional,
        'element': {
            'type': 'plain_text_input',
            'placeholder': {
                'type': 'plain_text',
                'text': 'Ask something'
            }
        },
        'label': {
            'type': 'plain_text',
            'text': f'Question #{num}',
            'emoji': True
        }
    }
