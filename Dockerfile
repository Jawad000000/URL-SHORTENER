FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Render injects PORT at runtime; default to 8000 for local Docker
# Migrations run first, then the server starts
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
