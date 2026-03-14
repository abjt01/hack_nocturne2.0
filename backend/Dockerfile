FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Create tables/schemas then start uvicorn
CMD ["sh", "-c", "PYTHONPATH=. python3 -c 'from app.database import create_tables; create_tables()' && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
