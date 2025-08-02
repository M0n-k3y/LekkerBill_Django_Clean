# F:/Python Apps/LekkerBill_Django_Clean/Dockerfile

# Use an official Python runtime as a parent image. 'slim' is a smaller version.
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and to run in unbuffered mode.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system-level dependencies.
# We need weasyprint's dependencies, its font library, AND the postgresql client.
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libpangoft2-1.0-0 \
    postgresql-client \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching.
COPY requirements.txt /app/

# Install the Python packages.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container.
COPY . /app/