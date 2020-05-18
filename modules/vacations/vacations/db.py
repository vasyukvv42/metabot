from datetime import date, datetime, time
from typing import List, Dict

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection  # noqa
from pymongo import ASCENDING


async def save_request(
        history: AsyncIOMotorCollection,
        request_type: str,
        date_from: date,
        date_to: date,
        reason: str,
        user_id: str
) -> str:
    datetime_from = datetime.combine(date_from, time.min)
    datetime_to = datetime.combine(date_to, time.min)
    result = await history.insert_one({
        'user_id': user_id,
        'type': request_type,
        'date_from': datetime_from,
        'date_to': datetime_to,
        'reason': reason,
        'approval_status': 'unapproved'
    })
    return str(result.inserted_id)


async def update_request_status(
        history: AsyncIOMotorCollection,
        request_id: str,
        status: str,
        admin_id: str
) -> None:
    await history.update_one({'_id': ObjectId(request_id)}, {
        '$set': {'approval_status': status, 'admin_id': admin_id}
    })


async def get_request_by_id(
        history: AsyncIOMotorCollection,
        request_id: str
) -> Dict:
    request = await history.find_one({'_id': ObjectId(request_id)})
    return request


async def get_request_history_by_user_id(
        history: AsyncIOMotorCollection,
        user_id: str
) -> List[Dict]:
    return await (
        history
        .find({'user_id': user_id})
        .sort('date_from', ASCENDING)
        .to_list(None)
    )
