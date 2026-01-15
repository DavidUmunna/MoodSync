from collections.abc import AsyncIterator
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users
from app.routers import auth
from app.routers import sessions
from app.routers import analytics
from app.routers import recommendation
from app.routers import ai
from app.routers import onboarding
from app.core.redis_Client import connect_redis, redisClient
from tortoise.contrib.fastapi import register_tortoise
from app.tortoise_config import TORTOISE_ORM



async def life_span(app: FastAPI) -> AsyncIterator[None]:

    await connect_redis()
    try:
        # Startup: try to connect Redis
        await connect_redis()
        print("✅ Redis connected")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
       
    yield  

app = FastAPI(title="MoodSync",lifespan=life_span)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(HTTPException)
async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"^http://(localhost|127\\.0\\.0\\.1):5173$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(analytics.router)
app.include_router(recommendation.router)
app.include_router(ai.router)
app.include_router(onboarding.router)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # Automatically create tables
    add_exception_handlers=True
)


@app.get("/")
def root():
    return {"message": "Welcome to your FastAPI backend!"}
