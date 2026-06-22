from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

import apis.utils.exceptions as exc
from constants.paths import AuthRoutes

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl=AuthRoutes.LOGIN
)


# Hash password
def hash_password(password: str):
    return pwd_context.hash(password)


# Verify password
def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# Create access token
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# Create refresh token
def create_refresh_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now() + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# Decode token
def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except JWTError:
        raise exc.UnauthorizedException(
            message="Invalid or expired token",
            error_code="INVALID_TOKEN"
        )


# Get current authenticated user
def get_current_user(
    token: str = Depends(oauth2_bearer)
):
    payload = decode_token(token)

    user_id = payload.get("user_id")

    if user_id is None:
        raise exc.UnauthorizedException(
            message="User ID not found in token",
            error_code="USER_NOT_FOUND"
        )

    return user_id