import time
import uuid

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from core import res
from core.constant import REQUEST_ID, TRACE_ID, REQUEST_ID_HEADER, TRACE_ID_HEADER, PROCESS_TIME_HEADER, CONTEXT_DATA
from core.tools import set_context, get_context

def app_with_middleware(app:FastAPI,funcs):
    for func in funcs:
        func(app)


def request_id_middleware(app:FastAPI):
    @app.middleware("http")
    async def _request_id_middleware(request:Request, call_next):
        id = uuid.uuid4()
        request.state.id = id
        set_context(request,REQUEST_ID,f"{id}")
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = str(id)
        return response

def trace_id_middleware(app:FastAPI):
    @app.middleware("http")
    async def _trace_id_middleware(request:Request, call_next):
        trace_id = uuid.uuid4()
        set_context(request,TRACE_ID,f"{trace_id}")
        response = await call_next(request)
        response.headers[TRACE_ID_HEADER] = str(trace_id)
        return response

def real_time_middleware(app:FastAPI):
    @app.middleware("http")
    async def _real_time_middleware(request:Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers[PROCESS_TIME_HEADER] = str(process_time)
        return response

def cors_middleware(app:FastAPI):
    @app.middleware("http")
    async def _cors_middleware(request:Request, call_next):
        headers = {
            "Access-Control-Allow-Credentials": "true",
        }
        origin = request.headers.get("Origin")
        if origin:
            headers["Access-Control-Allow-Origin"] = origin
        method = request.method
        if method == "OPTIONS":
            req_headers = request.headers.get("Access-Control-Request-Headers")
            req_methods = request.headers.get("Access-Control-Request-Methods")
            if req_headers:
                headers["Access-Control-Allow-Methods"] = req_methods
            if req_methods:
                headers["Access-Control-Allow-Headers"] = req_headers
            headers["Access-Control-Max-Age"] = "86400"
            return Response(status_code=204, headers=headers)
        response = await call_next(request)
        for key, value in headers.items():
            response.headers[key] = value
        return response

def exception_middleware(app:FastAPI):
    @app.middleware("http")
    async def _exception_middleware(request:Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            error_data = get_context(request,CONTEXT_DATA)
            return res.error(e,error_data)


def global_exception_handler(app:FastAPI):
    # 全局异常处理
    # 不通过中间件注册，直接在全局异常处理函数中捕获异常
    # 缺失trace_id,request_id等信息
    @app.exception_handler(Exception)
    async def _global_exception_handler(request: Request, exc: Exception):
        error_data = get_context(request, CONTEXT_DATA)
        return res.error(exc,error_data)