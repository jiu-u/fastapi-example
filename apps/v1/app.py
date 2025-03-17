from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette.requests import Request

from apps.v1 import deps
from apps.v1.deps import User, get_current_user
from apps.v1.endpoints import openai, openai_mock
from core import middleware, res, errors

app = FastAPI()

middleware.app_with_middleware(app,[
    middleware.exception_middleware,
    middleware.request_id_middleware,
    middleware.trace_id_middleware,
    middleware.real_time_middleware,
    middleware.cors_middleware,
])

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/token",response_model=Token,tags=["默认"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    ok,token = deps.validate_user(form_data.username,form_data.password)
    if not ok:
        return res.error(errors.Unauthorized,data="invalid username or password")
    return {"access_token": deps.get_ticket(), "token_type": "bearer"}


@app.get("/state",tags=["默认"])
async def read_state(request: Request,token: Annotated[str, Depends(deps.oauth2_scheme)]):
    return res.success(data={"request_id": str(request.state.id), "token": token})

@app.get("/",tags=["默认"])
async def read_root():
    return b"v1 server is running!"

@app.get("/health",response_model=res.BaseResponse[dict[str,str]],tags=["默认"])
async def read_health():
    return res.success(data={"message": "health check success"})

@app.get("/users/me",tags=["AUTH"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

class Pagination(BaseModel):
    page: int = 1
    per_page: int = 10
    sort: str = "created_at"
    order: str = "desc"



@app.get("/pagination",tags=["PAGINATION"])
async def read_pagination(pagination: Annotated[Pagination, Depends(Pagination)]):
    return res.success(data={"message": "pagination success"})

@app.get("/ticket1",tags=["AUTH"])
async def read_users_me2(current_user: User = Depends(deps.get_current_user_by_ticket)):
    return current_user
@app.get("/ticket2",description="错误的❌，无法在文档中携带token，应该使用原生的auth",tags=["AUTH"])
async def read_ticket2(current_user: User = Depends(deps.get_current_user_by_ticket2)):
    return res.success(data={"message": "ticket2 success"})

@app.get("/ticket3",description="错误的❌，无法在文档中携带token，应该使用原生的auth",tags=["AUTH"])
async def read_ticket3(current_user: User = Depends(deps.get_current_user_by_ticket3)):
    return res.success(data={"message": "ticket3 success"})

@app.get("/ticket4",description="错误的❌，无法在文档中携带token，应该使用原生的auth",tags=["AUTH"])
async def read_ticket4(current_user: User = Depends(deps.get_current_user_by_ticket4)):
    return res.success(data=current_user)
app.include_router(openai.router, prefix="", tags=["openai"],dependencies=[Depends(deps.get_current_user)])
app.include_router(openai_mock.router, prefix="/mock", tags=["openai_mock"])