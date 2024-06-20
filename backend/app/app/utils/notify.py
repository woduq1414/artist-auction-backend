from uuid import UUID
from redis.asyncio import Redis
import json

from app.schemas.notify_schema import INotifyCreate


async def make_notify(redis: Redis, message: INotifyCreate):
    # 
    recipent_id_list = message.receiver_id
    
    json_message = message.json()
    print(json_message, "@!#")
    dump_message = json.dumps(json_message)
    print(dump_message)
    
    if type(recipent_id_list) == str:
        pass
    else:
        for recipent_id in recipent_id_list:
            notify_key = f"notify:{recipent_id}"
            await redis.rpush(notify_key, json_message)
            
    
    
    await redis.publish("notify_channel", json_message)
    return {"message": "Notification sent"}


async def get_notify(redis : Redis, account_id : UUID, is_read : bool = False):
    notify_key = f"notify:{account_id}"
    notify_read_key = f"notify:read:{account_id}"
    
    messages = await redis.lrange(notify_key, 0, -1)
    
    if messages:
        data = [json.loads(message) for message in messages]
        
        if is_read:
            await redis.set(notify_read_key, data[-1].get("created_at"))
            
        return data
    else : 
        return []
    
    

async def delete_notify(redis: Redis, account_id: UUID, notify : INotifyCreate):
    notify_key = f"notify:{account_id}"
    
    await redis.lrem(notify_key, 0, notify.json())
    
    
async def delete_notify_all(redis: Redis, account_id: UUID):
    notify_key = f"notify:{account_id}"
    
    await redis.delete(notify_key)