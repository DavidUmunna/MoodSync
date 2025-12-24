from fastapi import FastAPI, Request, HTTPException
import time 
from app.core.redis_Client import redisClient as r

WINDOW_SECONDS=60
LIMIT=100

async def get_key(req: Request):
    # use email/username from request body or fallback to IP
    try:
        body = await req.json()
        return body.get("username", req.client.host)
    except:
        return req.client.host

async def rate_limiter(request: Request, call_next):
    key = await get_key(request)
    current_time = int(time.time())

    # Redis key for user/IP
    redis_key = f"rate_limit:{key}"

    # Increment count
    count = r.get(redis_key)
    if count is None:
        r.set(redis_key, 1, ex=WINDOW_SECONDS)  # expires in 30 mins
    elif int(count) < LIMIT:
        r.incr(redis_key)
    else:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    response = await call_next(request)
    return response