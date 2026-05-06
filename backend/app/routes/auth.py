from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb import get_database
from app.models.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

router = APIRouter(tags=["Authentication"])
security_scheme = HTTPBearer()


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserRegisterRequest,
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    """Register a new user account with secure password hashing."""
    user = await database["users"].find_one({"username": request.username})
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    hashed_password = hash_password(request.password)
    await database["users"].insert_one(
        {
            "username": request.username,
            "hashed_password": hashed_password,
        }
    )

    return {"message": "User registered successfully"}


@router.post("/auth/login", response_model=TokenResponse)
async def login_user(
    request: UserLoginRequest,
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    """Authenticate credentials and return a signed JWT access token."""
    user = await database["users"].find_one({"username": request.username})
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token({"sub": request.username})
    return TokenResponse(access_token=access_token)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    database: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    """Dependency to extract, decode, and authorize a secure Bearer JWT token."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await database["users"].find_one({"username": username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
