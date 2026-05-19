from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from src.db.database import get_session
from src.db.redis import add_jti_to_blocklist
from .service import User_service
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from .schemas import UserAccount, UserResponse, User_Login
from .utils import create_access_token, verify_password
from .dependencies import AccessTokenBearer, RefreshTokenBearer
from datetime import timedelta, datetime
from src.rate_limiter import rate_limit

auth_router = APIRouter()
user_service = User_service()
REFRESH_TOKEN_EXPIRY = 2
refresh_token_bearer = RefreshTokenBearer()


@auth_router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_new_user(
    user_data: UserAccount, session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="user already exists"
        )

    new_user = await user_service.create_user(user_data, session)
    return new_user


@auth_router.post("/login")
async def login_user(
    user_data: User_Login,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(rate_limit),
):
    email = user_data.email
    password = user_data.password

    user_exists = await user_service.get_user(email, session)

    if user_exists:
        pass_verified = verify_password(password, user_exists.password_hash)

        if pass_verified:
            access_token = create_access_token(
                user_data={"email": str(user_exists.email), "id": str(user_exists.id)}
            )

            refresh_token = create_access_token(
                user_data={"email": str(user_exists.email), "id": str(user_exists.id)},
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
                refresh=True,
            )

            return JSONResponse(
                content={
                    "message": "login succesful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user_exists.email, "id": user_exists.id},
                }
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalid data")


@auth_router.get("/refresh_token")
async def refresh_access_token(token_details: dict = Depends(refresh_token_bearer)):
    expiry = token_details["exp"]

    if datetime.fromtimestamp(expiry) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid token")


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):

    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK
    )
