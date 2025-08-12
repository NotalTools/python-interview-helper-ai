from typing import Dict, Literal
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения с использованием Pydantic Settings"""
    
    # Telegram Bot Token
    telegram_bot_token: str = Field(..., description="Telegram Bot Token от @BotFather")
    
    # AI Provider Settings
    ai_provider: str = Field(default="openai", description="AI провайдер: openai или gigachat")
    
    # OpenAI API Key
    openai_api_key: str = Field(default="", description="OpenAI API Key")
    
    # GigaChat Settings
    gigachat_client_id: str = Field(default="", description="GigaChat Client ID")
    gigachat_client_secret: str = Field(default="", description="GigaChat Client Secret")
    gigachat_auth_url: str = Field(default="https://ngw.devices.sberbank.ru:9443/api/v2/oauth", description="GigaChat Auth URL")
    gigachat_api_url: str = Field(default="https://gigachat.devices.sberbank.ru/api/v1", description="GigaChat API URL")
    
    # Настройки бота
    bot_name: str = Field(default="Interview Helper Bot", description="Название бота")
    
    # Настройки базы данных
    database_url: str = Field(
        default="sqlite+aiosqlite:///./interview_bot.db",
        description="URL базы данных"
    )
    
    # Настройки сервера
    host: str = Field(default="0.0.0.0", description="Хост для FastAPI сервера")
    port: int = Field(default=8000, description="Порт для FastAPI сервера")
    
    # Настройки логирования
    log_level: str = Field(default="INFO", description="Уровень логирования")

    # Админ токен для CRUD операций над вопросами (простой вариант)
    admin_token: str = Field(default="", description="Админ-токен для управления вопросами")

    # Лимиты
    daily_limit_per_user: int = Field(default=50, description="Дневной лимит оценок ответов на пользователя")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Константы приложения
class AppConstants:
    """Константы приложения"""
    
    # Уровни сложности
    LEVELS: Dict[str, str] = {
        "junior": "Junior",
        "middle": "Middle", 
        "senior": "Senior"
    }
    
    # Категории вопросов
    CATEGORIES: Dict[str, str] = {
        "system_design": "System Design",
        "algorithms": "Algorithms & Data Structures",
        "databases": "Databases",
        "networking": "Networking",
        "security": "Security",
        "backend": "Backend Development"
    }
    
    # Типы вопросов
    QUESTION_TYPES: Dict[str, str] = {
        "text": "Text Answer",
        "voice": "Voice Answer",
        "multiple_choice": "Multiple Choice"
    }

    # Мультиагентные пайплайны для интервью по категориям
    # Имя агента → конкретный класс определяется в интервью-оркестраторе
    INTERVIEW_CATEGORY_PIPELINES: Dict[str, list[str]] = {
        "system_design": [
            "architect",
            "storage",
            "reliability",
            "tradeoffs",
        ],
        "algorithms": [
            "alg_taskmaster",
            "alg_complexity",
            "alg_testgen",
            "alg_optimizer",
        ],
        "databases": [
            "db_modeler",
            "db_query_optimizer",
            "db_consistency",
            "db_replication",
        ],
        "networking": [
            "net_protocols",
            "net_latency",
            "net_lb",
            "net_chaos",
        ],
        "security": [
            "sec_threats",
            "sec_secure_code",
            "sec_crypto",
            "sec_compliance",
        ],
        "backend": [
            "be_api",
            "be_perf",
            "be_reliability",
            "be_obs",
        ],
    }


# Создаем экземпляр настроек
settings = Settings() 