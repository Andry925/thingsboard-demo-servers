FROM python:3.11-slim AS build

# Update package lists and install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev build-essential libssl-dev libffi-dev zlib1g-dev libxml2 libxslt-dev\
    && rm -rf /var/lib/apt/lists/*

# Copy the application code and configuration
ADD ./ /

# Set environment variables
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH=.

EXPOSE 4840

# Install Python packages
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade setuptools && \
    python3 -m pip install --no-cache-dir importlib_metadata && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the remaining files
COPY . .

# Set the container command
CMD [ "python", "./server.py" ]
