from datetime import datetime
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    """Базовая модель пользователя"""
    telegram_id: int = Field(..., description="Telegram ID пользователя")
    username: Optional[str] = Field(None, description="Username пользователя")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")


class UserCreate(UserBase):
    """Модель для создания пользователя"""
    pass


class UserUpdate(BaseModel):
    """Модель для обновления пользователя"""
    level: Optional[str] = Field(None, description="Уровень пользователя")
    category: Optional[str] = Field(None, description="Категория вопросов")
    current_question_id: Optional[int] = Field(None, description="ID текущего вопроса")
    score: Optional[int] = Field(0, description="Общий счет")
    questions_answered: Optional[int] = Field(0, description="Количество отвеченных вопросов")


class User(UserBase):
    """Полная модель пользователя"""
    id: int = Field(..., description="ID пользователя в БД")
    level: Optional[str] = Field(None, description="Уровень пользователя")
    category: Optional[str] = Field(None, description="Категория вопросов")
    current_question_id: Optional[int] = Field(None, description="ID текущего вопроса")
    score: int = Field(0, description="Общий счет")
    questions_answered: int = Field(0, description="Количество отвеченных вопросов")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")
    
    model_config = ConfigDict(from_attributes=True)


class QuestionBase(BaseModel):
    """Базовая модель вопроса"""
    title: str = Field(..., description="Заголовок вопроса")
    content: str = Field(..., description="Содержание вопроса")
    level: str = Field(..., description="Уровень сложности")
    category: str = Field(..., description="Категория вопроса")
    question_type: str = Field(..., description="Тип вопроса")
    points: int = Field(..., description="Количество баллов за правильный ответ")


class QuestionCreate(QuestionBase):
    """Модель для создания вопроса"""
    correct_answer: str = Field(..., description="Правильный ответ")
    explanation: Optional[str] = Field(None, description="Объяснение ответа")
    hints: Optional[List[str]] = Field(None, description="Подсказки")
    tags: Optional[List[str]] = Field(None, description="Теги вопроса")


class Question(QuestionBase):
    """Полная модель вопроса"""
    id: int = Field(..., description="ID вопроса")
    correct_answer: str = Field(..., description="Правильный ответ")
    explanation: Optional[str] = Field(None, description="Объяснение ответа")
    hints: Optional[List[str]] = Field(None, description="Подсказки")
    tags: Optional[List[str]] = Field(None, description="Теги вопроса")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")
    
    model_config = ConfigDict(from_attributes=True)


class AnswerBase(BaseModel):
    """Базовая модель ответа"""
    user_id: int = Field(..., description="ID пользователя")
    question_id: int = Field(..., description="ID вопроса")
    answer_text: str = Field(..., description="Текст ответа")
    answer_type: Literal["text", "voice"] = Field(..., description="Тип ответа")


class AnswerCreate(AnswerBase):
    """Модель для создания ответа"""
    voice_file_id: Optional[str] = Field(None, description="ID голосового файла в Telegram")


class Answer(AnswerBase):
    """Полная модель ответа"""
    id: int = Field(..., description="ID ответа")
    score: Optional[int] = Field(None, description="Полученный балл")
    feedback: Optional[str] = Field(None, description="Обратная связь")
    voice_file_id: Optional[str] = Field(None, description="ID голосового файла в Telegram")
    created_at: datetime = Field(..., description="Дата создания")
    
    model_config = ConfigDict(from_attributes=True)


class UserStats(BaseModel):
    """Модель статистики пользователя"""
    user_id: int = Field(..., description="ID пользователя")
    total_score: int = Field(0, description="Общий счет")
    questions_answered: int = Field(0, description="Количество отвеченных вопросов")
    average_score: float = Field(0.0, description="Средний балл")
    level: Optional[str] = Field(None, description="Текущий уровень")
    category: Optional[str] = Field(None, description="Текущая категория")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")


class QuestionRequest(BaseModel):
    """Модель запроса на получение вопроса"""
    level: str = Field(..., description="Уровень сложности")
    category: str = Field(..., description="Категория вопроса")
    exclude_ids: Optional[List[int]] = Field(None, description="ID вопросов для исключения")


class AnswerEvaluation(BaseModel):
    """Модель для оценки ответа"""
    answer_id: int = Field(..., description="ID ответа")
    score: int = Field(..., description="Полученный балл")
    feedback: str = Field(..., description="Обратная связь")
    is_correct: bool = Field(..., description="Правильность ответа")


class TelegramWebhook(BaseModel):
    """Модель для Telegram webhook"""
    update_id: int = Field(..., description="ID обновления")
    message: Optional[Dict] = Field(None, description="Сообщение")
    callback_query: Optional[Dict] = Field(None, description="Callback query") 