FROM eclipse-mosquitto AS build

# Update package lists and install necessary dependencies
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Copy the application code and configuration
ADD ./ /

EXPOSE 1883

# Set environment variables
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH=.

# Install Python packages
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade setuptools && \
    python3 -m pip install --no-cache-dir importlib_metadata && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the remaining files
COPY . .

# Set the container command
CMD ["sh", "-c", "mosquitto -c /mosquitto/config/mosquitto.conf & python3 publisher.py"]
