# ============================================
# AUTHENTICATION UTILITIES
# ============================================

from passlib.context import CryptContext

from jose import jwt

from datetime import (
    datetime,
    timedelta
)

import secrets

import os

from dotenv import load_dotenv


# ============================================
# LOAD ENVIRONMENT
# ============================================

load_dotenv()


# ============================================
# PASSWORD HASHING
# ============================================

pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto"

)


def hash_password(
    password: str
) -> str:

    return pwd_context.hash(
        password
    )


def verify_password(

    plain_password: str,

    hashed_password: str

) -> bool:

    return pwd_context.verify(

        plain_password,

        hashed_password

    )


# ============================================
# JWT
# ============================================

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY"
)


if not SECRET_KEY:

    raise RuntimeError(
        "JWT_SECRET_KEY not found in .env"
    )


ALGORITHM = "HS256"


ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ============================================
# CREATE ACCESS TOKEN
# ============================================

def create_access_token(
    user_id: int
):

    expire = (
        datetime.utcnow()
        +
        timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )


    payload = {

        "user_id":
        user_id,

        "exp":
        expire

    }


    token = jwt.encode(

        payload,

        SECRET_KEY,

        algorithm=ALGORITHM

    )


    return token


# ============================================
# OTP UTILITIES
# ============================================

def generate_otp() -> str:

    return str(

        secrets.randbelow(
            900000
        ) + 100000

    )


def hash_otp(
    otp: str
) -> str:

    return pwd_context.hash(
        otp
    )


def verify_otp(

    otp: str,

    otp_hash: str

) -> bool:

    return pwd_context.verify(

        otp,

        otp_hash

    )