FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# Expose dummy port (required by platform)
EXPOSE 8080

CMD ["python", "main.py"]
