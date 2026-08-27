FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY src ./src
COPY dashboard ./dashboard

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 neotrader \
    && mkdir -p /app/runtime \
    && chown -R neotrader:neotrader /app

USER neotrader

EXPOSE 8000

CMD ["python", "-m", "neotrader.dashboard_server"]
