# Базовый образ с Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Отключаем буферизацию вывода Python (важно для консольных приложений в Docker)
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Единая папка данных (volume), эталонные JSON и доп. каталоги для импорта
ENV DATA_DIR=/app/data
ENV IMPORT_DIRS=/app/im_port

# Создаём папки для данных и seed
RUN mkdir -p /app/data /app/seed

# Сначала зависимости — ради кэша слоёв
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Код проекта (включая im_port/*.json)
COPY . .

# Эталонная БД — по отдельному пути, чтобы volume её не перекрывал
COPY seed/ /app/seed/

# Entrypoint: засеет /app/data из seed только если в /app/data пусто
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

CMD ["python", "main.py"]