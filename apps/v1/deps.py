from typing import Union, List, Optional

from fastapi import Depends
from fastapi.params import Header
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from pydantic import BaseModel
from starlette.requests import Request

from core import errors, tools, constant
from core.tools import set_context

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

default_ticket = "linuxdo"


def set_ticket(ticket: str):
    global default_ticket
    default_ticket = ticket


def get_ticket():
    return default_ticket


fake_users_db = {
    "admin": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
}


def validate_user(username: str, password: str) -> (bool, str):
    user = fake_users_db.get(username)
    if not user:
        return False, ""
    if not password == "123456":
        return False, ""
    return True, get_ticket()


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, token: str):
    if token == get_ticket():
        username = "admin"
        if username in db:
            user_dict = db[username]
            return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        tools.set_context(request, constant.CONTEXT_DATA, "token is invalid")
        raise errors.Unauthorized
    return user


def check_permission(permissions: List[str]):
    async def _check_permission(current_user: User = Depends(get_current_user)):
        # 获取用户
        # 检查权限
        return current_user

    return _check_permission


security = HTTPBearer()


async def get_current_user_by_ticket(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    print(credentials)
    return


async def get_current_user_by_ticket2(
    request: Request, authorization: str = Header(None)
):
    print(authorization)
    return


async def get_current_user_by_ticket3(
    x_token: Optional[str] = Header(None, alias="Authorization"),
):
    print(x_token)
    return


async def get_current_user_by_ticket4(request: Request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        set_context(request, constant.CONTEXT_DATA, "token is required")
        raise errors.Unauthorized
    token = authorization.removeprefix("Bearer ")
    if not token:
        set_context(request, constant.CONTEXT_DATA, "token is required")
        raise errors.Unauthorized
    if token != get_ticket():
        set_context(request, constant.CONTEXT_DATA, "token is invalid")
        raise errors.Unauthorized
    return fake_decode_token(token)
