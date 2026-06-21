from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import apis.utils.exceptions as exc

from apis.config.database import get_db
from apis.models.db_models.db_user_model import DBUser
from apis.models.local_models.auth_model import (
    SignupModel,
    LoginModel,
    RefreshModel
)
from apis.models.local_models.api_response_model import ApiResponse
from apis.services.jwt_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from constants.paths import AuthRoutes, prefix

router = APIRouter(prefix=prefix, tags=["Auth"])


# Signup
@router.post(AuthRoutes.SIGNUP, response_model=ApiResponse)
def signup(user: SignupModel, db: Session = Depends(get_db)):

    existing_user = db.query(DBUser).filter(
        DBUser.email == user.email.strip().lower()
    ).first()

    if existing_user:
        raise exc.ConflictException(
            message="Email already exists",
            error_code="EMAIL_EXISTS"
        )

    new_user = DBUser(
        name=user.name,
        email=user.email.strip().lower(),
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return ApiResponse(
        success=True,
        message="Signup successful",
        data={"user_id": new_user.id}
    )


# Login
@router.post(AuthRoutes.LOGIN, response_model=ApiResponse)
def login(user: LoginModel, db: Session = Depends(get_db)):

    db_user = db.query(DBUser).filter(
        DBUser.email == user.email.strip().lower()
    ).first()

    if not db_user:
        raise exc.NotFoundException(
            message="User not found",
            error_code="USER_NOT_FOUND"
        )

    if not verify_password(user.password, db_user.password):
        raise exc.UnauthorizedException(
            message="Invalid password",
            error_code="INVALID_PASSWORD"
        )

    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    return ApiResponse(
        success=True,
        message="Login successful",
        data={
            "id": db_user.id,
            "name": db_user.name,
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    )

# Refresh token
@router.post(AuthRoutes.REFRESH, response_model=ApiResponse)
def refresh_token(data: RefreshModel):

    payload = decode_token(data.refresh_token)

    if not payload:
        raise exc.UnauthorizedException(
            message="Invalid or expired refresh token",
            error_code="INVALID_TOKEN"
        )

    new_access_token = create_access_token(
        {"sub": payload["sub"]}
    )

    return ApiResponse(
        success=True,
        message="Token refreshed successfully",
        data={"access_token": new_access_token}
    )