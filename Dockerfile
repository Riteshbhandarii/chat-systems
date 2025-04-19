# Use official Python 3.9 image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Create and set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Collect static files (if needed)
RUN python manage.py collectstatic --noinput

# Run Daphne ASGI server
CMD ["daphne", "-b", "0.0.0.0", "--port", "$PORT", "chat_project.asgi:application"]