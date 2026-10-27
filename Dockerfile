# 1. Start from an official image that already has Python
FROM python:3.12-slim

# 2. Settings: show logs immediately, use UTF-8 text
ENV PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1

# 3. All our files go into /app inside the container
WORKDIR /app

# 4. Install libraries first (cached if requirements.txt doesn't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the project
COPY . .

# 6. Default command: start the API
EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]