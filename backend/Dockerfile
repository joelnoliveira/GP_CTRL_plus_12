FROM python:3.13-slim

ARG USER_NAME="not-admin"

ENV USER_NAME $USER_NAME

# Set the working directory in the container
# WORKDIR /workspace
WORKDIR /backend

# add non root user
RUN adduser --disabled-password --gecos "" $USER_NAME


COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Switch to non-root
USER $USER_NAME
