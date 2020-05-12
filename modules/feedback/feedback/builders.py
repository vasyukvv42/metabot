from typing import Dict, List

from feedback.config import (
    TITLE_INPUT_ACTION_ID,
    RECIPIENTS_SELECT_ACTION_ID,
    CREATION_VIEW_ID,
    QUESTION_INPUT_ACTION_ID,
    NOTIFY_ACTION_ID,
    ANSWER_ACTION_ID, ANSWER_VIEW_ID, ANSWER_INPUT_ACTION_ID
)

DIVIDER = {
    'type': 'divider'
}


def build_creation_view(num_of_questions: int) -> Dict:
    blocks = [
        {
            'type': 'input',
            'block_id': 'title',
            'element': {
                'type': 'plain_text_input',
                'action_id': TITLE_INPUT_ACTION_ID,
                'max_length': 24
            },
            'label': {
                'type': 'plain_text',
                'text': 'Title',
                'emoji': True
            }
        },
        {
            'type': 'input',
            'block_id': 'recipients',
            'element': {
                'type': 'multi_users_select',
                'action_id': RECIPIENTS_SELECT_ACTION_ID,
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
        build_question_input()
    ]
    for question_number in range(2, num_of_questions + 1):
        blocks.append(build_question_input(question_number, True))
    return {
        'type': 'modal',
        'callback_id': CREATION_VIEW_ID,
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


def build_answer_view(title: str, questions: List[str], q_id: str) -> Dict:
    blocks = [{
        'type': 'input',
        'block_id': f'answer_{num}',
        'element': {
            'type': 'plain_text_input',
            'action_id': ANSWER_INPUT_ACTION_ID.format(num),
            'multiline': True
        },
        'label': {
            'type': 'plain_text',
            'text': question,
            'emoji': True
        }
    } for num, question in enumerate(questions, start=1)]

    return {
        'type': 'modal',
        'callback_id': ANSWER_VIEW_ID,
        'private_metadata': q_id,
        'title': {
            'type': 'plain_text',
            'text': title,
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


def build_question_input(num: int = 1, optional: bool = False) -> Dict:
    return {
        'type': 'input',
        'optional': optional,
        'block_id': f'question_{num}',
        'element': {
            'type': 'plain_text_input',
            'action_id': QUESTION_INPUT_ACTION_ID.format(num),
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


def build_control_message(
        q_id: str,
        questions: List[str],
        recipients: List[str],
        title: str
) -> List[Dict]:
    formatted_recipients = ' '.join(f'<@{user_id}>' for user_id in recipients)
    formatted_questions = '\n'.join(
        f'*Question #{num}:* {q}' for num, q in enumerate(questions, start=1)
    )
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': 'Your questionnaire has been sent out to every '
                        'recipient! Here is what was sent just in case you '
                        'forget:'
            }
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*Title:*\n{title}\n'
                        f'*Recipients:*\n{formatted_recipients}\n'
                        f'{formatted_questions}'
            }
        },
        DIVIDER,
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': 'You can click on this button if someone is taking too '
                        'long.'
            },
            'accessory': {
                'type': 'button',
                'action_id': NOTIFY_ACTION_ID,
                'style': 'primary',
                'text': {
                    'type': 'plain_text',
                    'text': 'Notify',
                    'emoji': True
                },
                'value': q_id
            }
        }
    ]


def build_answer_message(author: str, q_id: str, title: str) -> List[Dict]:
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'<@{author}> is asking for your feedback on '
                        f'*"{title}"*!\n'
                        f'Click on the button to answer some questions.'
            },
            'accessory': {
                'type': 'button',
                'style': 'primary',
                'action_id': ANSWER_ACTION_ID,
                'text': {
                    'type': 'plain_text',
                    'text': 'Answer',
                    'emoji': True
                },
                'value': q_id
            }
        }
    ]


def build_submitted_feedback_message(
        author: str,
        questions: List[str],
        answers: List[str]
) -> List[Dict]:
    blocks: List[Dict] = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'<@{author}> has submitted feedback!'
            }
        }
    ]
    for q, a in zip(questions, answers):
        blocks.append(DIVIDER)
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*Q:* {q}\n*A:* {a}'
            }
        })
    return blocks
