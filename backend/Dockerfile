FROM python:3.11-slim

ARG USER_NAME="not-admin"

ENV USER_NAME $USER_NAME

# Set the working directory in the container
# WORKDIR /workspace
WORKDIR /backend

# add non root user
RUN adduser --disabled-password --gecos "" $USER_NAME


COPY pyproject.toml requirements.txt ./

# Copy the current directory contents into the container at /app
COPY . .

# Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt && \
#     pip install --no-cache-dir .
RUN pip install --no-cache-dir -e .

# Switch to non-root
USER $USER_NAME
