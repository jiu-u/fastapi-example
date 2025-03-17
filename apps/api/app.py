from fastapi import FastAPI

from core import res

app = FastAPI()


@app.get("/")
async def read_root():
    return b"api v1 server is running!"


@app.get("/health", response_model=res.BaseResponse[dict[str, str]])
async def read_health():
    return res.success(data={"message": "health check success"})
