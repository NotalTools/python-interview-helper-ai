# Interview Helper Bot

Telegram бот для подготовки к техническим собеседованиям с использованием AI для оценки ответов.

## 🎯 Возможности

- **Выбор уровня сложности**: Junior, Middle, Senior
- **Разнообразные категории**: System Design, Algorithms, Databases, Networking, Security, Backend
- **Два типа ответов**: Текстовые и голосовые сообщения
- **AI-оценка**: Автоматическая оценка ответов с помощью OpenAI GPT-4
- **Статистика**: Отслеживание прогресса и результатов
- **FastAPI**: REST API для интеграции с другими системами

## 🏗️ Архитектура

```
src/
├── config.py          # Конфигурация с Pydantic Settings
├── models.py          # Pydantic модели данных
├── database.py        # SQLAlchemy модели и работа с БД
├── services.py        # Бизнес-логика (OpenAI, вопросы, ответы)
├── api.py            # FastAPI приложение
└── telegram_bot.py   # Telegram бот
```

### Технологический стек

- **FastAPI** - современный веб-фреймворк
- **Pydantic** - валидация данных и настройки
- **SQLAlchemy** - ORM для работы с базой данных
- **python-telegram-bot** - Telegram Bot API
- **OpenAI** - AI для оценки ответов и транскрипции
- **uv** - быстрый пакетный менеджер

## 🚀 Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd python-interview-helper-ai
```

### 2. Установка зависимостей

```bash
# Установка uv (если не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка зависимостей
uv sync
```

### 3. Настройка переменных окружения

Создайте файл `.env` на основе `env.example`:

```bash
cp env.example .env
```

Заполните необходимые переменные:

```env
# Telegram Bot Token (получите у @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# AI Provider (openai или gigachat)
AI_PROVIDER=openai

# OpenAI API Key (получите на https://platform.openai.com/)
OPENAI_API_KEY=your_openai_api_key_here

# GigaChat Settings (получите на https://developers.sber.ru/portal/products/gigachat)
GIGACHAT_CLIENT_ID=your_gigachat_client_id_here
GIGACHAT_CLIENT_SECRET=your_gigachat_client_secret_here

# Настройки бота
BOT_NAME=Interview Helper Bot

# Настройки базы данных (по умолчанию SQLite)
DATABASE_URL=sqlite+aiosqlite:///./interview_bot.db

# Настройки сервера
HOST=0.0.0.0
PORT=8000

# Настройки логирования
LOG_LEVEL=INFO
```

### 4. Получение токенов

#### Telegram Bot Token
1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env`

#### AI Provider Setup

**OpenAI:**
1. Зарегистрируйтесь на [OpenAI Platform](https://platform.openai.com/)
2. Перейдите в раздел API Keys
3. Создайте новый ключ
4. Скопируйте ключ в `.env`

**GigaChat:**
1. Зарегистрируйтесь на [Sber Developers Portal](https://developers.sber.ru/portal/products/gigachat)
2. Создайте приложение и получите Client ID и Client Secret
3. Скопируйте данные в `.env`
4. Установите `AI_PROVIDER=gigachat` в `.env`

### 5. Запуск приложения

```bash
# Запуск бота и API сервера одновременно
python main.py

# Или только бота
python main.py --mode bot

# Или только API сервера
python main.py --mode api
```

## 📱 Использование бота

### Основные команды

- `/start` - Начать работу с ботом
- `/help` - Показать справку
- `/stats` - Показать статистику
- `/settings` - Настройки профиля

### Процесс работы

1. **Выбор уровня**: Junior, Middle или Senior
2. **Выбор категории**: System Design, Algorithms, Databases, Networking, Security, Backend
3. **Получение вопроса**: Бот задает случайный вопрос
4. **Ответ**: Отправьте текстовое или голосовое сообщение
5. **Оценка**: Получите AI-оценку с обратной связью
6. **Повтор**: Получите следующий вопрос

## 🔧 API Endpoints

### Пользователи
- `GET /users/{telegram_id}` - Получить пользователя
- `POST /users/` - Создать пользователя
- `PUT /users/{telegram_id}` - Обновить пользователя
- `GET /users/{telegram_id}/stats` - Статистика пользователя

### Вопросы
- `GET /questions/{question_id}` - Получить вопрос
- `POST /questions/random` - Случайный вопрос
- `POST /questions/` - Создать вопрос

### Ответы
- `POST /answers/text` - Отправить текстовый ответ
- `POST /answers/voice` - Отправить голосовой ответ

### Вспомогательные
- `GET /levels` - Доступные уровни
- `GET /categories` - Доступные категории
- `GET /health` - Проверка здоровья сервиса

## 🗄️ База данных

По умолчанию используется SQLite. Для продакшена рекомендуется PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

### Миграции

Для управления миграциями используется Alembic:

```bash
# Создание миграции
alembic revision --autogenerate -m "Description"

# Применение миграций
alembic upgrade head
```

## 🧪 Тестирование

```bash
# Запуск тестов
uv run pytest

# С покрытием кода
uv run pytest --cov=src
```

## 📊 Мониторинг

- Логи сохраняются в `bot.log`
- FastAPI автоматически генерирует документацию на `/docs`
- Health check endpoint: `GET /health`

## 🔒 Безопасность

- Все API ключи хранятся в переменных окружения
- Валидация данных с помощью Pydantic
- SQL injection защита через SQLAlchemy
- CORS настройки для API

## 🚀 Развертывание

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync --frozen

CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  bot:
    build: .
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/interview_bot
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: interview_bot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License

## 📞 Поддержка

Если у вас есть вопросы или проблемы, создайте Issue в репозитории. 

## 🧑‍🏫 Мультиагентный Python‑наставник (MVP)

- Агенты: Преподаватель, Примерщик, Тренер, Код‑ревьюер, Мотиватор
- Оркестратор: простой раунд‑робин через `PythonMentorOrchestrator`
- Исполнение кода: Piston API (эндпоинт `/python/sessions/{id}/run`)
- Создание сессии: `POST /python/sessions` (возвращает первый раунд ответов агентов)

Пример тела запроса:

```json
{ "user_id": 123, "level": "junior", "topic": "Работа с API в Python" }
``` 