FROM python:latest

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY ../pyproject.toml ../uv.lock* ../requirements.txt* ./
COPY ../app/ .

RUN uv sync --frozen

CMD ["uv", "run", "python", "main.py"]
