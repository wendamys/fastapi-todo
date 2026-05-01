FROM python:3.12-slim

# Устанавливаем зависимости для драйвера Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

EXPOSE 8000

# Запуск через fastapi run (для продакшна) или uvicorn
CMD ["fastapi", "run", "main.py", "--port", "8000"]
