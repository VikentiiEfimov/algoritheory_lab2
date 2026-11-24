# Базовый образ с Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Отключаем буферизацию вывода Python (важно для консольных приложений в Docker)
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Указываем Python, где брать данные внутри контейнера
ENV DATA_DIR=/app/data

# Создаём папку для данных, чтобы volume монтировался корректно
RUN mkdir -p /app/data

# Сначала копируем только requirements, чтобы кэш слоёв работал эффективнее
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код
COPY . .

# Команда запуска (по умолчанию интерактивная консоль)
CMD ["python", "main.py"]