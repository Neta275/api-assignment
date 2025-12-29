# 1. Linux-based Python image
FROM python:3.12-slim

# Install curl inside the image so we can run health-check from Jenkins with `docker exec`
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Set working directory inside the container
WORKDIR /app

# 3. Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the project files into the container
COPY . .

# 5. Run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
