from redis.asyncio import Redis

redisClient = Redis(host="localhost", port=6379, decode_responses=True)


async def connect_redis():
    try:
        pong = await redisClient.ping()
        if pong:
            print("✅ Connected to Redis!")
    except Exception as e:
        print("❌ Failed to connect:", e)
