import asyncio
import json
import time
import uuid
from typing import Any, Dict, AsyncGenerator

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from core import res

router = APIRouter()


@router.get("/state")
def raise_error(request: Request):
    return res.success(data={"request_id": str(request.state.id)})


@router.post("/chat/completions")
async def open_chat_completions(request: Request):
    try:
        body = await request.json()
        is_stream = body.get("stream", False)

        if not is_stream:
            resp_data = await gen_json_data(body)
            return JSONResponse(status_code=200, content=resp_data)
        else:
            stream_generator = await mock_third_party_api()
            return StreamingResponse(
                parse_third_party_stream(stream_generator),
                media_type="text/event-stream",
            )
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})


async def gen_json_data(body):
    return {
        "id": "chatcmpl-BBvTN7D3DpW4MBv9WDCd3aoJkzk2Y",
        "object": "chat.completion",
        "created": 1742182233,
        "model": "gpt-4o-mini-2024-07-18",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "你好，这是一条测试消息！",
                    "refusal": None,
                },
                "logprobs": None,
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 15,
            "completion_tokens": 406,
            "total_tokens": 421,
            "prompt_tokens_details": {"cached_tokens": 0, "audio_tokens": 0},
            "completion_tokens_details": {
                "reasoning_tokens": 0,
                "audio_tokens": 0,
                "accepted_prediction_tokens": 0,
                "rejected_prediction_tokens": 0,
            },
        },
        "system_fingerprint": "fp_ded0d14823",
    }


async def mock_third_party_api() -> AsyncGenerator[Dict[str, Any], None]:
    user_message = "Hello"

    async def stream_generator() -> AsyncGenerator[Dict[str, Any], None]:
        response_text = f"This is a mock streaming response to: {user_message}. "
        response_text += "I'll count from 1 to 5 to demonstrate streaming capability. "
        response_text += "One. Two. Three. Four. Five."

        chunks = response_text.split(". ")

        for i, chunk in enumerate(chunks):
            if not chunk:
                continue

            chunk_data = {
                "chunk_id": i,
                "content": chunk + (". " if i < len(chunks) - 1 else "") + "\n",
                "is_final": i == len(chunks) - 1,
                "sequence": i,
            }

            yield chunk_data
            await asyncio.sleep(0.5)  # Simulate network delay

    return stream_generator()


async def parse_third_party_stream(
    stream_generator: AsyncGenerator[Dict[str, Any], None],
) -> AsyncGenerator[str, None]:
    response_id = f"chatcmpl-{uuid.uuid4()}"
    async for third_party_data in stream_generator:
        try:
            openai_format = {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "mock-model",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": third_party_data["content"]},
                        "finish_reason": "stop"
                        if third_party_data.get("is_final", False)
                        else None,
                    }
                ],
            }
            yield f"data: {json.dumps(openai_format)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    yield "data: [DONE]\n\n"
