from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings, AppConstants
from .database import database
from .models import (
    User, UserCreate, UserUpdate, UserStats,
    Question, QuestionCreate, QuestionRequest,
    Answer, AnswerCreate, AnswerEvaluation,
    TelegramWebhook
)
from .services import (
    UserService, QuestionService, AnswerService, 
    VoiceService, OpenAIService
)
from .container import get_interview_app_service
from .routers.python_tutor import router as python_tutor_router
from .container import (
    get_user_app_service,
    get_question_app_service,
    get_answer_app_service,
    get_tutor_app_service,
)
from .rate_limit import limiter
from .domain.entities import QuestionEntity

# Настройка логирования
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Подключение к базе данных при запуске
    await database.connect()
    await database.create_tables()
    logger.info("База данных подключена и таблицы созданы")
    
    yield
    
    # Отключение от базы данных при остановке
    await database.disconnect()
    logger.info("База данных отключена")


# Создание FastAPI приложения
app = FastAPI(
    title="Interview Helper Bot API",
    description="API для Telegram бота подготовки к техническим собеседованиям",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение нового роутера
app.include_router(python_tutor_router)


# Эндпоинты для пользователей
@app.get("/users/{telegram_id}", response_model=User)
async def get_user(telegram_id: int):
    """Получение пользователя по Telegram ID"""
    users = get_user_app_service()
    user = await users.get_or_create(telegram_id, None, None, None)
    return user


@app.post("/users/", response_model=User)
async def create_user(user_data: UserCreate):
    """Создание нового пользователя"""
    users = get_user_app_service()
    user = await users.get_or_create(
        user_data.telegram_id,
        user_data.username,
        user_data.first_name,
        user_data.last_name,
    )
    return user


@app.put("/users/{telegram_id}", response_model=User)
async def update_user(telegram_id: int, user_data: UserUpdate):
    """Обновление пользователя"""
    users = get_user_app_service()
    update_data = user_data.dict(exclude_unset=True)
    updated_user = await users.get_or_create(telegram_id, None, None, None)
    if "level" in update_data:
        updated_user = await users.update_level(telegram_id, update_data["level"]) or updated_user
    if "category" in update_data:
        updated_user = await users.update_category(telegram_id, update_data["category"]) or updated_user
    return updated_user


@app.get("/users/{telegram_id}/stats", response_model=UserStats)
async def get_user_stats(telegram_id: int):
    """Получение статистики пользователя"""
    users = get_user_app_service()
    stats = await users.stats(telegram_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return stats


# Эндпоинты для вопросов
@app.get("/questions/{question_id}", response_model=Question)
async def get_question(question_id: int):
    """Получение вопроса по ID"""
    question = await QuestionService.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    return question


@app.post("/questions/random", response_model=Question)
async def get_random_question(request: QuestionRequest):
    """Получение случайного вопроса"""
    qs = get_question_app_service()
    # Используем фиктивного telegram_id=0? Лучше передавать из клиента, но для MVP оставим
    question = await qs.random_for_user(0, request.level, request.category)
    if not question:
        raise HTTPException(
            status_code=404, 
            detail=f"Вопросы для уровня {request.level} и категории {request.category} не найдены"
        )
    return question


@app.post("/questions/", response_model=Question)
async def create_question(question_data: QuestionCreate):
    """Создание нового вопроса"""
    # Простой админ-токен
    from fastapi import Header
    # В FastAPI нельзя добавлять параметры после объявления функции — делаем отдельный handler ниже
    pass


@app.post("/admin/questions", response_model=Question)
async def admin_create_question(question_data: QuestionCreate, x_admin_token: str | None = Header(default=None)):
    if not settings.admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="unauthorized")
    question = Question(
        title=question_data.title,
        content=question_data.content,
        level=question_data.level,
        category=question_data.category,
        question_type=question_data.question_type,
        points=question_data.points,
        correct_answer=question_data.correct_answer,
        explanation=question_data.explanation,
        hints=question_data.hints,
        tags=question_data.tags
    )
    qs = get_question_app_service()
    created = await qs.create(question)
    return created


@app.put("/admin/questions/{question_id}", response_model=Question)
async def admin_update_question(question_id: int, question_data: QuestionCreate, x_admin_token: str | None = Header(default=None)):
    if not settings.admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="unauthorized")
    # Простая реализация: создаём как новый объект c тем же id (для MVP)
    entity = QuestionEntity(
        id=question_id,
        title=question_data.title,
        content=question_data.content,
        level=question_data.level,
        category=question_data.category,
        question_type=question_data.question_type,
        points=question_data.points,
        correct_answer=question_data.correct_answer,
        explanation=question_data.explanation,
        hints=question_data.hints,
        tags=question_data.tags,
    )
    entity.validate()
    qs = get_question_app_service()
    updated = await qs.update(question_id, question_data.model_dump(exclude_unset=True))
    return updated


@app.delete("/admin/questions/{question_id}")
async def admin_delete_question(question_id: int, x_admin_token: str | None = Header(default=None)):
    if not settings.admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="unauthorized")
    # Для MVP: удаление напрямую через сессию ORM
    qs = get_question_app_service()
    ok = await qs.delete(question_id)
    return {"status": "deleted" if ok else "not_found", "id": question_id}


@app.get("/admin/questions", response_model=list[Question])
async def admin_search_questions(level: str | None = None, category: str | None = None, q: str | None = None, limit: int = 20, offset: int = 0, x_admin_token: str | None = Header(default=None)):
    if not settings.admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="unauthorized")
    qs = get_question_app_service()
    res = await qs.search(level, category, q, limit, offset)
    return res


# Эндпоинты для ответов
@app.post("/answers/text", response_model=AnswerEvaluation)
async def submit_text_answer(
    user_id: int,
    question_id: int,
    answer_text: str,
    background_tasks: BackgroundTasks
):
    """Отправка текстового ответа"""
    try:
        if not limiter.allow(user_id):
            raise HTTPException(status_code=429, detail="Daily limit exceeded")
        # Через application layer (DDD) — использует порты/адаптеры
        app_service = get_interview_app_service()
        answer, evaluation = await app_service.answer_text(user_id, question_id, answer_text)
        return evaluation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при обработке текстового ответа: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.post("/answers/voice", response_model=AnswerEvaluation)
async def submit_voice_answer(
    user_id: int,
    question_id: int,
    voice_file_id: str,
    background_tasks: BackgroundTasks
):
    """Отправка голосового ответа"""
    try:
        if not limiter.allow(user_id):
            raise HTTPException(status_code=429, detail="Daily limit exceeded")
        app_answers = get_answer_app_service()
        answer, evaluation = await app_answers.answer_voice(
            user_id, question_id, voice_file_id, settings.telegram_bot_token
        )
        return evaluation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обработке голосового ответа: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


# Эндпоинт для Telegram webhook
@app.post("/webhook/telegram")
async def telegram_webhook(webhook_data: TelegramWebhook):
    """Webhook для получения обновлений от Telegram"""
    # Здесь будет логика обработки сообщений от Telegram
    # Пока просто логируем
    logger.info(f"Получен webhook: {webhook_data}")
    return {"status": "ok"}


# Вспомогательные эндпоинты
@app.get("/levels")
async def get_levels():
    """Получение доступных уровней"""
    return AppConstants.LEVELS


@app.get("/categories")
async def get_categories():
    """Получение доступных категорий"""
    return AppConstants.CATEGORIES


@app.get("/question-types")
async def get_question_types():
    """Получение типов вопросов"""
    return AppConstants.QUESTION_TYPES


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "database": "connected" if database.engine else "disconnected"
    }


# Вспомогательные функции
async def cleanup_temp_files(*file_paths):
    """Очистка временных файлов"""
    import os
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Ошибка при удалении файла {file_path}: {e}")


# Создание директории для временных файлов
import os
os.makedirs("temp", exist_ok=True) 