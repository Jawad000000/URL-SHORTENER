import logging
import uuid

from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from ..config import Config


passwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def generate_password_hash(password: str):
    password_byte = password.encode("utf-8")[:72]
    return passwd_context.hash(password_byte)

def verify_password(password: str, password_hash: str) -> bool:
    password_byte= password.encode("utf-8")[:72]
    return passwd_context.verify(password_byte, password_hash)

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    payload={
        'user': user_data,
        'exp': datetime.now() + (expiry if expiry is not None else timedelta(minutes=60)),
        'jti': str(uuid.uuid4()),
        'refresh': refresh
    }

    token = jwt.encode(
        payload=payload,
        key = Config.JWT_SECRET,
        algorithm= Config.JWT_ALGORITHM
    )
    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key = Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )

        return token_data
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None

    except Exception as e:
        logging.exception(e)
        return None
