FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

WORKDIR /build
RUN python -m venv /opt/venv
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AEGIS_DATA_DIR=/app/data \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

RUN groupadd --system aegis && useradd --system --gid aegis --create-home aegis
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY aegis ./aegis
COPY pyproject.toml requirements.txt ./

RUN mkdir -p /app/data && chown -R aegis:aegis /app
USER aegis

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"

CMD ["uvicorn", "aegis.api:app", "--host", "0.0.0.0", "--port", "8000"]
