import pytest
from datetime import timedelta
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

def test_password_hashing_and_verification():
    password = "my_secure_password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_invalid_hash_verification():
    assert verify_password("password", "invalid_hash_string") is False

def test_create_and_decode_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert token is not None
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "testuser"

def test_create_access_token_with_expiry():
    data = {"sub": "anotheruser"}
    expiry = timedelta(minutes=5)
    token = create_access_token(data, expires_delta=expiry)
    assert token is not None
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "anotheruser"

def test_decode_invalid_token():
    assert decode_access_token("invalid.token.string") is None
