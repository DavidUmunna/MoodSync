from fastapi import APIRouter, status, HTTPException, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User
from app.core.database import get_db
from pydantic import BaseModel, EmailStr
import uuid
import os
import regex as re
import bcrypt
import hashlib
from app.middlewares.ratelimiter import rate_limiter
from app.core.redis_Client import redisClient
import json


window_seconds = 30 * 60
limit = 100

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/cache-test")
async def cache_test():
    await redisClient.set("key", "value")
    val = await redisClient.get("key")
    return {"cached_value": val}


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with SHA256 pre-hashing."""
    prehashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(prehashed.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    prehashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return bcrypt.checkpw(prehashed.encode('utf-8'), hashed_password.encode('utf-8'))


class userCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.get("/")
async def get_users():
    # A dummy
    return [{"id": 1, "name": "John Doe"}]


@router.post("/createuser", status_code=status.HTTP_201_CREATED)
async def CreateUser(user: userCreate, db: AsyncSession = Depends(get_db)):
    try:
        # SQLAlchemy: Check if user exists
        result = await db.execute(
            select(User).where(User.email == user.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash the password
        hashed_password = hash_password(user.password)

        # SQLAlchemy: Create new user
        new_user = User(
            first_name=user.firstname,
            last_name=user.lastname,
            email=user.email,
            password_hash=hashed_password
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)  # Refresh to get the generated user_id

        return {
            "message": "User created successfully",
            "user": {
                "id": str(new_user.user_id),
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email
            }
        }
    except HTTPException as httperror:
        raise httperror
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/signin", dependencies=[Depends(rate_limiter)])
async def userSignIn(
    request: LoginRequest, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    try:
        # Validate email format
        if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}$", request.email):
            raise HTTPException(
                400,
                detail="the username you entered is not valid"
            )
        
        # SQLAlchemy: Get user from database
        result = await db.execute(
            select(User).where(User.email == request.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user was not found"
            )

        # Verify password
        if not verify_password(request.password, existing_user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create session
        sessionId = uuid.uuid4()

        json_string = json.dumps({
            "userId": str(existing_user.user_id),
            "email": existing_user.email,
            "firstName": existing_user.first_name,
            "lastName": existing_user.last_name,
        })

        await redisClient.set(
            f"session:{sessionId}",
            json_string,
            ex=1200
        )

        env = os.getenv("NODE_ENV", "development")
        same_site = "none" if env == "production" else "lax"
        secure = env == "production"
    
        response.set_cookie(
            key="sessionId",
            value=str(sessionId),
            httponly=True,
            max_age=20 * 60,
            samesite=same_site,
            secure=secure
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "userId": str(existing_user.user_id),
                "email": existing_user.email,
                "firstName": existing_user.first_name,
                "lastName": existing_user.last_name,
                "createdAt": existing_user.createdAt.isoformat()
            }
        }

    except HTTPException as httperror:
        raise httperror
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server Error: {str(e)}"
        )


@router.post("/signout")
async def SignOut(
    request: Request, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    try:
        data = await request.json()
        user_id = data.get("userId")

        # Validate userId format (UUID)
        try:
            user_uuid = uuid.UUID(user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="userId is not valid")

        # SQLAlchemy: Check if user exists
        result = await db.execute(
            select(User).where(User.user_id == user_uuid)
        )
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            raise HTTPException(status_code=404, detail="User Id not found")

        # Delete the Redis session
        existing_session = await redisClient.delete(f"session:{user_id}")
        if not existing_session:
            raise HTTPException(status_code=404, detail="No session with matching ID")

        print("User logged out:", user_id)

        # Clear the sessionId cookie
        env = os.getenv("NODE_ENV", "development")
        response.delete_cookie(
            key="sessionId",
            httponly=True,
            secure=(env == "production"),
            samesite="none" if env == "production" else "lax"
        )

        return {"success": True, "message": "Logged out and session cleared"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print("Logout error:", e)
        raise HTTPException(status_code=500, detail="Server error detected")