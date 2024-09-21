# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for the app user
RUN mkdir /app
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the project files
COPY . /app/


# Expose port 8000 for the app
EXPOSE 8000

# Define the default command to run the app
CMD ["python manage.py migrate && python manage.py collectstatic --noinput && gunicorn phoenix.wsgi:application --bind 0.0.0.0:8000"]



