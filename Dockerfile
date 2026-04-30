# Используем официальный легкий образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл со списком библиотек
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы вашего проекта (main.py, data.json и т.д.) в контейнер
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Команда для запуска (используем fastapi run для "боевого" режима в контейнере)
CMD ["fastapi", "run", "main.py", "--port", "8000"]