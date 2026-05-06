# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Upgrade pip and pre-install legacy setuptools to avoid openai-whisper build errors
RUN pip install --no-cache-dir --upgrade pip setuptools==69.0.3

# Copy requirements first to leverage Docker's caching mechanism
COPY requirements.txt /app/

# Install python dependencies (using --no-build-isolation to let setuptools 69.0.3 be used during whisper build)
RUN pip install --no-cache-dir -r requirements.txt --no-build-isolation

# Copy the rest of the backend application code
COPY . /app/

# Create folders for uploads and vector stores to persist data
RUN mkdir -p uploads vector_store

# Expose the API port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
