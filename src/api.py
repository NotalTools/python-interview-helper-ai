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
from .routers.python_tutor import router as python_tutor_router

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
    user = await database.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@app.post("/users/", response_model=User)
async def create_user(user_data: UserCreate):
    """Создание нового пользователя"""
    existing_user = await database.get_user_by_telegram_id(user_data.telegram_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    user = await UserService.get_or_create_user(
        user_data.telegram_id,
        user_data.username,
        user_data.first_name,
        user_data.last_name
    )
    return user


@app.put("/users/{telegram_id}", response_model=User)
async def update_user(telegram_id: int, user_data: UserUpdate):
    """Обновление пользователя"""
    user = await database.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    update_data = user_data.dict(exclude_unset=True)
    updated_user = await database.update_user(telegram_id, **update_data)
    if not updated_user:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении пользователя")
    
    return updated_user


@app.get("/users/{telegram_id}/stats", response_model=UserStats)
async def get_user_stats(telegram_id: int):
    """Получение статистики пользователя"""
    stats = await UserService.get_user_stats(telegram_id)
    if stats.user_id == 0:
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
    question = await database.get_random_question(
        request.level, 
        request.category, 
        request.exclude_ids
    )
    if not question:
        raise HTTPException(
            status_code=404, 
            detail=f"Вопросы для уровня {request.level} и категории {request.category} не найдены"
        )
    return question


@app.post("/questions/", response_model=Question)
async def create_question(question_data: QuestionCreate):
    """Создание нового вопроса"""
    # Здесь можно добавить проверку прав доступа
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
    
    async with database.get_session() as session:
        session.add(question)
        await session.commit()
        await session.refresh(question)
    
    return question


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
        answer_service = AnswerService()
        answer, evaluation = await answer_service.process_text_answer(
            user_id, question_id, answer_text
        )
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
        # Скачиваем голосовой файл
        voice_service = VoiceService()
        ogg_path = f"temp/{voice_file_id}.ogg"
        wav_path = f"temp/{voice_file_id}.wav"
        
        success = await voice_service.download_voice_file(
            voice_file_id, settings.telegram_bot_token, ogg_path
        )
        if not success:
            raise HTTPException(status_code=400, detail="Не удалось скачать голосовое сообщение")
        
        # Конвертируем в WAV
        success = await voice_service.convert_ogg_to_wav(ogg_path, wav_path)
        if not success:
            raise HTTPException(status_code=400, detail="Не удалось обработать аудио файл")
        
        # Обрабатываем ответ
        answer_service = AnswerService()
        answer, evaluation = await answer_service.process_voice_answer(
            user_id, question_id, wav_path, voice_file_id
        )
        
        # Очищаем временные файлы
        background_tasks.add_task(cleanup_temp_files, ogg_path, wav_path)
        
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