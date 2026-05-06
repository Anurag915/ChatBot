import pytest
from httpx import AsyncClient
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.routes.auth import get_current_user
from app.utils.security import hash_password, create_access_token

@pytest.mark.asyncio
async def test_auth_register_success(async_client: AsyncClient, mock_db):
    response = await async_client.post(
        "/auth/register",
        json={"username": "newuser", "password": "securepassword"}
    )
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"
    
    # Check database
    user = await mock_db["users"].find_one({"username": "newuser"})
    assert user is not None

@pytest.mark.asyncio
async def test_auth_register_duplicate(async_client: AsyncClient, mock_db):
    await mock_db["users"].insert_one({"username": "existinguser", "hashed_password": "hashed"})
    
    response = await async_client.post(
        "/auth/register",
        json={"username": "existinguser", "password": "securepassword"}
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_auth_login_success(async_client: AsyncClient, mock_db):
    hashed = hash_password("mypassword")
    await mock_db["users"].insert_one({"username": "loginuser", "hashed_password": hashed})
    
    response = await async_client.post(
        "/auth/login",
        json={"username": "loginuser", "password": "mypassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_auth_login_incorrect_credentials(async_client: AsyncClient, mock_db):
    hashed = hash_password("mypassword")
    await mock_db["users"].insert_one({"username": "loginuser", "hashed_password": hashed})
    
    response = await async_client.post(
        "/auth/login",
        json={"username": "loginuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_current_user_valid(mock_db):
    hashed = hash_password("mypassword")
    await mock_db["users"].insert_one({"username": "tokenuser", "hashed_password": hashed})
    token = create_access_token({"sub": "tokenuser"})
    
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await get_current_user(credentials=credentials, database=mock_db)
    assert user is not None
    assert user["username"] == "tokenuser"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db):
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalidtoken")
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials=credentials, database=mock_db)
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_user_not_found(mock_db):
    token = create_access_token({"sub": "nonexistent"})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials=credentials, database=mock_db)
    assert exc.value.status_code == 401
