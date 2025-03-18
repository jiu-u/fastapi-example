# 使用官方 Python 作为基础镜像，选择一个适合你的项目的版本
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 将当前目录的内容复制到工作目录中
COPY . /app

# 安装项目所需的 Python 依赖
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple  \
    && pip install --no-cache-dir -r requirements.txt

# 暴露 FastAPI 默认的运行端口
EXPOSE 8000

# 使用 Uvicorn 作为 ASGI 服务器来运行 FastAPI 应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
