from fastapi import APIRouter,status,HTTPException,Depends,Response,Request
from passlib.context import CryptContext
from app.models.users import User
from odmantic import AIOEngine
from pydantic import BaseModel,EmailStr
import uuid
import os
import regex as re
import bcrypt
from app.middlewares.ratelimiter import rate_limiter
from app.core.redis_Client import redisClient
import json



window_seconds=30*60
limit=100

router = APIRouter(prefix="/users", tags=["Users"])
engine=AIOEngine()



@router.get("/cache-test")
async def cache_test():
    await redisClient.set("key", "value")
    val = await redisClient.get("key")
    return {"cached_value": val}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class userCreate(BaseModel):
    firstname:str
    lastname:str
    email:EmailStr
    password:str

@router.get("/")
async def get_users():
    #A dummy
    return [{"id": 1, "name": "John Doe"}]

@router.get("/")
async def getUserData():
    try:
       return {"message":"this is a message"}

    except HTTPException as httperror:
        return httperror
    




@router.post("/createuser",status_code=status.HTTP_201_CREATED)
async def CreateUser(user:userCreate):
    try:
        existing_user=await  engine.find_one(User,User.email==user.email)
        if(existing_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        hashed_password=pwd_context.hash(user.password)

        new_User=User(
            first_name=user.firstname,
            last_name=user.lastname,
            email=user.email,
            password_hash=hashed_password
        )

        await engine.save(new_User)

        return {
            "message": "User created successfully",
            "user": {
                "id": str(new_User.id),
                "first_name": new_User.first_name,
                "last_name": new_User.last_name,
                "email": new_User.email
            }
        }
    except HTTPException as httperror:
        raise httperror
    except Exception as e:
        # Catch any unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


class LoginRequest(BaseModel):
    email:EmailStr
    password:str
    


@router.post("/signin", dependencies=[Depends(rate_limiter)])
async def userSignIn(request:LoginRequest,response:Response):
    try:
        existing_user=await  engine.find_one(User,User.email==request.email)

        if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}$",request.email):
            raise HTTPException(
                400,
                detail="the username you entered is not valid"
            )
        if not existing_user :
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user was not found "
            )
        
        if not existing_user or not bcrypt.verify(request.password, existing_user["password"]):
           raise HTTPException(status_code=401, detail="Invalid email or password")


        
        sessionId=uuid.uuid4()

        json_string = json.dumps({
            "userId": existing_user["_id"],
            "role": existing_user["role"],
            "email": existing_user["email"],
            "name": existing_user["name"],
            "createdAt": existing_user["createdAt"]
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
            value=sessionId,
            httponly=True,
            max_age=20*60,
            samesite=same_site,
            secure=secure
        )
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "userId": existing_user["_id"],
                "role": existing_user["role"],
                "email": existing_user["email"],
                "name": existing_user["name"],
                "canApprove": existing_user["canApprove"],
                "Department": existing_user["Department"],
                "createdAt": existing_user["createdAt"].isoformat()  # convert datetime to ISO string
            }
         }

    

    except HTTPException as httperror:
        return httperror
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error"
        )


        
@router.post("/signout")
async def SignOut(request: Request, response: Response):
    try:
        data = await request.json()
        user_id = data.get("userId")

        # Validate userId format (24-char hex string)
        if not user_id or not re.fullmatch(r"[0-9A-Fa-f]{24}", user_id):
            raise HTTPException(status_code=400, detail="userId is not valid")

        # Check if admin user exists
        admin_user = await User.get_or_none(id=user_id)
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

           
        
        
        





    
