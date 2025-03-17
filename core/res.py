from typing import Generic, TypeVar, Optional

from pydantic import BaseModel
from starlette.responses import JSONResponse

from .errors import get_error

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    status_code: int
    code: int
    message: str
    data: Optional[T] = None


def success(
    data: Optional[T] = None,
    message: str = "success",
    code: int = 0,
    status_code: int = 200,
) -> JSONResponse:
    resp = BaseResponse[T](
        status_code=status_code, code=code, message=message, data=data
    )
    return JSONResponse(status_code=status_code, content=resp.model_dump())


def success_2(
    data: Optional[T] = None,
    message: str = "success",
    code: int = 0,
    status_code: int = 200,
) -> BaseResponse[T]:
    return BaseResponse[T](
        status_code=status_code, code=code, message=message, data=data
    )


def error(exc: Exception, data: Optional[T] = None) -> JSONResponse:
    e = get_error(exc)
    resp = BaseResponse[T](
        status_code=e.status_code, code=e.code, message=e.message, data=data
    )
    return JSONResponse(status_code=e.status_code, content=resp.model_dump())


def error_2(exc: Exception, data: Optional[T] = None) -> BaseResponse[T]:
    e = get_error(exc)
    return BaseResponse[T](
        status_code=e.status_code, code=e.code, message=e.message, data=data
    )
