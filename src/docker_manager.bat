@echo off
setlocal

:: Path to the Docker Compose executable
set DOCKER_COMPOSE_PATH=C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe

:: Navigate to the app directory
cd C:\path\to\your\django-app

:: Build and start the Docker container
%DOCKER_COMPOSE_PATH% down
%DOCKER_COMPOSE_PATH% pull
%DOCKER_COMPOSE_PATH% up --build -d

:: Clean up
endlocal
