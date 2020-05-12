from typing import List, Optional, Dict

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection  # noqa
from pymongo import ReturnDocument


async def save_questionnaire(
        collection: AsyncIOMotorCollection,
        user: str,
        title: str,
        recipients: List[str],
        questions: List[str]
) -> str:
    result = await collection.insert_one({
        'user_id': user,
        'title': title,
        'recipients': recipients,
        'questions': questions,
        'answers': {},
        'ts': None
    })
    return str(result.inserted_id)


async def update_questionnaire_ts(
        collection: AsyncIOMotorCollection,
        q_id: str,
        ts: Optional[str]
) -> None:
    await collection.update_one(
        {'_id': ObjectId(q_id)},
        {'$set': {'ts': ts}}
    )


async def get_questionnaire_by_id(
        collection: AsyncIOMotorCollection,
        q_id: str
) -> Optional[Dict]:
    questionnaire = await collection.find_one({'_id': ObjectId(q_id)})
    return questionnaire


async def update_questionnaire_answers(
        collection: AsyncIOMotorCollection,
        q_id: str,
        user_id: str,
        answers: List[str]
) -> Dict:
    return await collection.find_one_and_update(
        {'_id': ObjectId(q_id)},
        {'$set': {f'answers.{user_id}': answers}},
        return_document=ReturnDocument.AFTER
    )
