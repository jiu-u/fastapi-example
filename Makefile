.PHONY: dev
dev:
	uvicorn main:app --reload --port 8000

.PHONY: check
check:
	uv run ruff check

.PHONY: format
format:
	uv run ruff format

.PHONY: fix
fix:
	uv run ruff check --fix

.PHONY: exp
exp:
	uv export --format requirements-txt > requirements.txt

.PHONY: docker
docker:
	docker build -f ./Dockerfile  -t zywoo/fastapi-demo:v1 .
	docker run --rm -it -p 8000:8000 zywoo/fastapi-demo:v1

#docker buildx build --platform linux/arm64 -t zywoo/fastapi-demo-arm64:v1 .
# docker save zywoo/fastapi-demo-arm64:v1 -o dist.tar



