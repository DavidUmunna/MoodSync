from fastapi import FastAPI
from app.routers import users
from app.core.redis_Client import connect_redis, redisClient
from tortoise.contrib.fastapi import register_tortoise
from app.tortoise_config import TORTOISE_ORM



async def  life_span(app:FastAPI):

    await connect_redis()
    try:
        # Startup: try to connect Redis
        await connect_redis()
        print("✅ Redis connected")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
       
    yield  

app = FastAPI(title="MoodSync",lifespan=life_span)

# include routers
app.include_router(users.router)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # Automatically create tables
    add_exception_handlers=True
)


@app.get("/")
def root():
    return {"message": "Welcome to your FastAPI backend!"}
