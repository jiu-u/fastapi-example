import json

import httpx
from fastapi import APIRouter,Response
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

import dto
from core import res, errors

# 第一种：直接转发httpx.response ✅
# 第二种：解析数据，并返回序列化后的数据(流式、非流式)。请求转换，响应转换。✅
# 额外： mock数据 ✅


router = APIRouter()

API_KEY = "sk-1234567890"
API_URL = "https://api.openai.com/v1"

@router.get("/state")
async def open_read_state(request: Request):
    return res.success(data={"request_id": str(request.state.id)})

@router.post("/chat/completions")
async def open_chat_completions(request: Request,req: dto.ChatCompletionRequest):
    is_stream = False
    body = await request.json()
    if body.get("stream"):
        is_stream = True
    if not is_stream:
        resp_data = await oai_chat_completions(body)
        return JSONResponse(status_code=200, content=resp_data)
    else:
        third_party_response = await oai_chat_completions_stream(body)
        return StreamingResponse(
                parse_third_party_stream(third_party_response),
                media_type="text/event-stream"
            )

async def oai_chat_completions_stream(body):
    try:
        # 省略转换request
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL + "/chat/completions", json=body, headers={"Authorization": f"Bearer {API_KEY}"})
            return response
    except Exception as e:
        raise errors.InternalServerError

# 转换流式响应的格式函数
async def parse_third_party_stream(stream_response: httpx.Response):
    """Parse the third-party API's streaming response and convert to OpenAI format."""
    async for chunk in stream_response.aiter_lines():
        if not chunk or chunk.strip() == "":
            continue
        try:
            # Remove "data: " prefix if present (common in SSE)
            if chunk.startswith("data: "):
                chunk = chunk[6:]
            # Skip any heartbeat messages
            if chunk == "[DONE]" or chunk == "":
                continue
            # Parse the chunk (adjust based on third-party format)
            third_party_data = json.loads(chunk)
            openai_format = {
                **third_party_data,
                "owned_by": "x",
            }
            # Return as a Server-Sent Event
            yield f"data: {json.dumps(openai_format)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    # Send the final [DONE] message
    yield "data: [DONE]\n\n"

# 非流式
async def oai_chat_completions(body):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL + "/chat/completions", json=body, headers={"Authorization": f"Bearer {API_KEY}"})
            data = response.json()
            return mock_convert_json_format(data)
    except Exception as e:
        raise errors.InternalServerError

def mock_convert_json_format(data):
    return data

@router.get("/models")
async def open_models(request: Request):
    try:
        # 省略转换request
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL + "/models", headers={"Authorization": f"Bearer {API_KEY}"})
            json_data = response.json()
            return json_data
    except Exception as e:
        raise errors.InternalServerError

@router.post("/completions")
async def open_completions(request: Request):
    return await relay_openai_chat_completions(request,"/completions")

@router.post("/embeddings")
async def open_embeddings(request: Request):
    return await relay_openai_chat_completions(request,"/embeddings")

@router.post("/audio/speech")
async def open_audio_speech(request: Request):
    return await relay_openai_chat_completions(request,"/audio/speech")

@router.post("/audio/transcriptions")
async def open_audio_transcriptions(request: Request):
    return await relay_openai_chat_completions(request,"/audio/transcriptions")

@router.post("/audio/translations")
async def open_audio_translations(request: Request):
    return await relay_openai_chat_completions(request,"/audio/translations")

@router.post("/images/generations")
async def open_images_generations(request: Request):
    return await relay_openai_chat_completions(request,"/images/generations")

@router.post("/images/edits")
async def open_images_edits(request: Request):
    return await relay_openai_chat_completions(request,"/images/edits")

@router.post("/images/variations")
async def open_images_variations(request: Request):
    return await relay_openai_chat_completions(request,"/images/variations")

async def relay_openai_chat_completions(request: Request,path: str):
    headers = {
        "Content-Type": request.headers.get("Content-Type"),
        "Authorization": f"Bearer {API_KEY}",
        # "cache-control": "no-cache",
        "accept-encoding": "identity"
    }
    content_type = request.headers.get("Content-Type")
    if not content_type:
        raise errors.BadRequest
    if content_type == "application/json":
        data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL + path, json=data, headers=headers,timeout=30)
            # print(response.status_code,response.headers)
            return Response(
                status_code=response.status_code,
                content=response.content,
                headers=dict(response.headers),
                media_type=response.headers.get("Content-Type"),
            )
    elif content_type == "application/x-www-form-urlencoded":
        data = await request.form()
        form_data = dict(data)
        print(form_data)
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL + path, data=form_data, headers=headers,timeout=30)
            print(response.status_code,response.headers)
            return Response(
                status_code=response.status_code,
                content=response.content,
                headers=response.headers,
                media_type=response.headers.get("Content-Type"),
            )
    elif content_type.startswith("multipart/form-data"):
        # 多部分表单数据（包含文件）
        form_data = await request.form()

        # 创建多部分表单数据
        files = {}
        data = {}

        for key, value in form_data.items():
            # 检查是否为文件
            if hasattr(value, "filename"):
                # 是文件类型
                content = await value.read()
                files[key] = (value.filename, content, value.content_type)
            else:
                # 普通表单字段
                data[key] = value
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL + path, files=files, data=data, headers=headers,timeout=30)
            return Response(
                status_code=response.status_code,
                content=response.content,
                headers=response.headers,
                media_type=response.headers.get("Content-Type"),
            )
    else:
        raise errors.BadRequest





