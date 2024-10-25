# Use the official Python image as the base
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    libpango1.0-0 \
    libcairo2 \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-pango-1.0 \
    gir1.2-gtk-3.0 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Expose ports for Django and Celery
EXPOSE 8000 6379

# Add entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Define default command (handled in entrypoint.sh)
# CMD ["gunicorn", "phoenix.wsgi:application", "--bind", "0.0.0.0:8000"]
