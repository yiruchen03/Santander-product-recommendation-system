FROM python:3.9-slim

WORKDIR /app

# Avoids writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy application
COPY . /app

# Install build dependencies first (if any build required for lightgbm)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Create models folder if absent
RUN mkdir -p /app/models

EXPOSE 8000

# Use uvicorn for FastAPI production serving
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
