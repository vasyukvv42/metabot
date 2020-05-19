from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Dict, Iterable

from bson import ObjectId, Decimal128
from motor.motor_asyncio import AsyncIOMotorCollection  # noqa
from pymongo import DESCENDING
from pymongo.errors import BulkWriteError

from vacations.config import LEAVE_TYPES


async def save_request(
        history: AsyncIOMotorCollection,
        leave_type: str,
        date_from: date,
        date_to: date,
        duration: int,
        reason: str,
        user_id: str
) -> str:
    datetime_from = datetime.combine(date_from, time.min)
    datetime_to = datetime.combine(date_to, time.min)
    result = await history.insert_one({
        'user_id': user_id,
        'leave_type': leave_type,
        'date_from': datetime_from,
        'date_to': datetime_to,
        'duration': duration,
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


async def get_leaves_history_by_user_id(
        history: AsyncIOMotorCollection,
        user_id: str
) -> Iterable[Dict]:
    requests = await (
        history
        .find({'user_id': user_id, 'approval_status': 'approved'})
        .sort('date_from', DESCENDING)
        .limit(10)
        .to_list(None)
    )
    return reversed(requests)


async def get_days_by_user_id(
        users: AsyncIOMotorCollection,
        user_id: str,
) -> Dict[str, Decimal]:
    user = await users.find_one({'_id': user_id}) or {}
    days = user.get('days', {})
    return {
        leave_type: days.get(leave_type, Decimal128('0')).to_decimal()
        for leave_type in LEAVE_TYPES
    }


async def increase_days_by_user(
        users: AsyncIOMotorCollection,
        leave_type: str,
        days: Decimal,
        user_id: str,
) -> None:
    await users.update_one(
        {'_id': user_id},
        {'$inc': {f'days.{leave_type}': Decimal128(days)}},
        upsert=True
    )


async def increase_days(
        users: AsyncIOMotorCollection,
        leave_type: str,
        days: Decimal,
) -> None:
    await users.update_many(
        {},
        {'$inc': {f'days.{leave_type}': Decimal128(days)}}
    )


async def increase_days_by_config(
        users: AsyncIOMotorCollection,
        users_list: List[str],
) -> None:
    try:
        await users.insert_many(
            [{'_id': user_id} for user_id in users_list],
            ordered=False
        )
    except BulkWriteError:
        pass
    await users.update_many(
        {'_id': {'$in': users_list}},
        {
            '$inc': {
                f'days.{leave_type}': value
                for leave_type, value in LEAVE_TYPES.items()
            }
        }
    )


async def get_active_leaves(
        history: AsyncIOMotorCollection,
        current_date: date,
) -> List[Dict]:
    current_datetime = datetime.combine(current_date, time.min)
    return await (
        history.find({
            'date_from': {'$lte': current_datetime},
            'date_to': {'$gte': current_datetime},
            'approval_status': 'approved'
        }).to_list(None)
    )
