# Базовый образ с Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Отключаем буферизацию вывода Python (важно для консольных приложений в Docker)
ENV PYTHONUNBUFFERED=1

# Сначала копируем только requirements, чтобы кэш слоёв работал эффективнее
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код
COPY . .

# Создаём папку для данных, чтобы volume монтировался корректно
RUN mkdir -p /app/data

# Команда запуска (по умолчанию интерактивная консоль)
CMD ["python", "main.py"]