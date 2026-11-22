FROM python:3.10-slim-bookworm

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

ENTRYPOINT ["python", "src/simulate_recovery.py"]
