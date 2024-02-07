from functools import lru_cache
from typing import Annotated, Optional
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pocket import Pocket
from starlette.datastructures import URL

from app.settings import settings

security = HTTPBasic()


def get_current_token(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"bridge"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    is_correct_password = credentials.password in settings.user_tokens
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.password


def get_base_url(url: URL) -> URL:
    return url.replace(path='', query='', fragment='')


@lru_cache
def get_pocket_instance(request_token: str) -> Optional[Pocket]:
    access_token = settings.user_tokens[request_token]
    if access_token is None:
        return None

    return Pocket(
        consumer_key=settings.pocket_consumer_key,
        access_token=access_token
    )
