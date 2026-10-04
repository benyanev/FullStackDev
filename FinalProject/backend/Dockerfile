# Backend image — Flask API served by Gunicorn.
# Also used by the "agents" service (same code, different command).
# Build context is the project root (requirements.txt lives there).

FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so this layer is cached between code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 5000

# 1 process x 8 threads = 8 requests at the same time, so a slow AI request
# (~30 s) or a video download doesn't block the rest of the site.
# One process keeps the rate-limit counters (stored in memory) exact.
# 60 s timeout because AI requests can take ~30 s.
CMD ["gunicorn", "--workers", "1", "--threads", "8", "--bind", "0.0.0.0:5000", "--timeout", "60", "app:create_app()"]
