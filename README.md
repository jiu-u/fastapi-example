## 新建项目

```bash
uv init fastapi-example
# or
mkdir -p fastapi-example
cd ./fastapi-example
uv init --name fastapi-example -p 3.13

uv sync
```

## 配置镜像源

```toml
[[tool.uv.index]]
name = "tsinghua"
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
explicit = true
```

## 激活虚拟环境

```bash
# 在 macOS 和 Linux 上：
$ source .venv/bin/activate
# 在 Windows 上：
$ .venv\Scripts\activate
```

## 安装包

```bash
uv add fastapi httpx uvicorn pydantic python-dotenv python-multipart
```

## 运行

```bash
uv run main.py
```

或者

```bash
uvicorn main:app --reload --port 9999
```

