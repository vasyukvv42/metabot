from datetime import date, datetime, time
from typing import List, Dict

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection  # noqa
from pymongo import ASCENDING


async def save_request(
        collection: AsyncIOMotorCollection,
        date_from: date,
        date_to: date,
        reason: str,
        user_id: str
) -> str:
    datetime_from = datetime.combine(date_from, time.min)
    datetime_to = datetime.combine(date_to, time.min)
    result = await collection.insert_one({
        'user_id': user_id,
        'date_from': datetime_from,
        'date_to': datetime_to,
        'reason': reason,
        'approval_status': 'unapproved'
    })
    return str(result.inserted_id)


async def update_request_status(
        collection: AsyncIOMotorCollection,
        request_id: str,
        status: str,
        admin_id: str
) -> None:
    await collection.update_one({'_id': ObjectId(request_id)}, {
        '$set': {'approval_status': status, 'admin_id': admin_id}
    })


async def get_request_by_id(
        collection: AsyncIOMotorCollection,
        request_id: str
) -> Dict:
    request = await collection.find_one({'_id': ObjectId(request_id)})
    return request


async def get_request_history_by_user_id(
        collection: AsyncIOMotorCollection,
        user_id: str
) -> List[Dict]:
    return await (
        collection
        .find({'user_id': user_id})
        .sort('date_from', ASCENDING)
        .to_list(None)
    )
