# Sports Tournament Manager (Спортивная команда)

## Название
Sports Tournament Manager — консольный менеджер футбольного турнира на Python.

## Описание
Консольное приложение для управления футбольным турниром: команды, игроки,
матчи и расчёт статистики игрока / команды / турнира. Реализовано в рамках
лабораторной работы (вариант «Спортивная команда»: Команда, Игрок, Матч).

## Возможности
- создание команд и добавление игроков
  (позиции: Нападающий, Защитник, Вратарь, Полузащитник);
- фиксация матчей со счётом и статистикой игроков (голы + пасы);
- расчёт статистики игрока / команды / турнира;
- турнирная таблица, топ бомбардиров, разница мячей;
- экспорт отчёта в `.xlsx` (`openpyxl`);
- импорт данных из `.json`;
- сохранение/загрузка турнира в SQLite3;
- тесты на `pytest`.

## Структура проекта

```text
.
├── main.py            # Точка входа и главное меню
├── requirements.txt   # Зависимости проекта
├── Dockerfile         # Конфигурация Docker-образа
├── README.md          # Документация проекта
├── sports_package/    # Модели: BaseEntity, Player, Team, Match, Tournament
├── cn_port/           # Консольный интерфейс и вывод статистики
├── ex_port/           # Экспорт данных в Excel (.xlsx)
├── im_port/           # Импорт из JSON (loader.py и файлы данных)
├── bd_port/           # Работа с SQLite (database.py, tournament.db)
└── test_models.py     # Тесты моделей (pytest)
```

## Инструкции по запуску

### Локальный запуск
1. Клонируйте репозиторий и перейдите в папку проекта:
   ```bash

   git clone <repo-url>
   cd <project>

2. Создайте и активируйте виртуальное окружение:
   ```bash

   python -m venv .venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1

3. Установите зависимости:
   ```bash

   pip install -r requirements.txt

4. Запустите приложение:
   ```bash

   python main.py

### Тесты
   ```bash

   python -m pytest -v
   ```

### Запуск через Docker
Сборка образа:
   ```bash
   
   docker build -t sports-tournament .
   ```

### Тесты Запуск (флаг -it обязателен — приложение интерактивное и использует input()):
   ```bash

   docker run -it --rm sports-tournament
   ```

### Запуск с сохранением базы между перезапусками:
   ```bash

   docker run -it --rm -v "${PWD}:/app/data" sports-tournament
   ```

### Прогнать тесты в контейнере:
   ```bash

   docker run --rm sports-tournament pytest -v
   ```