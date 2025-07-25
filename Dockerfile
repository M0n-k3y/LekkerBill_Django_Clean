# Use an official Python runtime as a parent image. 'slim' is a smaller version.
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files and to run in unbuffered mode.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install the system-level dependencies required by weasyprint for PDF generation.
# This is the most direct and reliable method. This MUST run before any python code.
# We add the `--no-install-recommends` flag to keep the image small and `rm` the apt cache.
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching.
# This means Docker won't reinstall packages on every code change.
COPY requirements.txt /app/

# Install the Python packages.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container.
COPY . /app/

# NOTE: We do NOT run 'migrate' or 'gunicorn' here.
# This file's only job is to BUILD the image.
# Your Procfile will correctly handle running 'migrate' on release and 'gunicorn' to start the server.