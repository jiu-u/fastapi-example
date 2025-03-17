from fastapi import FastAPI

from apps import api, v1

app = FastAPI()

@app.get("/")
async def read_root():
    return b"server is running!"

app.mount("/api/v1",api.app)
app.mount("/v1",v1.app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
