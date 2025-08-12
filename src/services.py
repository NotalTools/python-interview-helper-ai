import asyncio
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from pydub import AudioSegment
import aiofiles
import aiohttp
from aiohttp import ClientTimeout

from .config import settings
from .interview_service import InterviewService
from .database import database
from .models import User, Question, Answer, UserStats, AnswerEvaluation
from .domain.rubrics import build_rubric_text

logger = logging.getLogger(__name__)


class AIService:
    """Базовый класс для AI сервисов"""
    
    async def evaluate_answer(self, question: Question, user_answer: str,
                              answer_type: str = "text",
                              multi_agent_notes: Optional[str] = None) -> AnswerEvaluation:
        """Оценка ответа пользователя"""
        raise NotImplementedError
    
    async def transcribe_voice(self, voice_file_path: str) -> str:
        """Транскрипция голосового сообщения"""
        raise NotImplementedError


class OpenAIService(AIService):
    """Сервис для работы с OpenAI API"""
    
    def __init__(self):
        # Настраиваем таймауты и базовые ретраи SDK
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=20.0,
            max_retries=2,
        )
        self._max_retries = 3
        self.docs_client = None  # Удалено по требованию
    
    async def evaluate_answer(self, question: Question, user_answer: str,
                            answer_type: str = "text",
                            multi_agent_notes: Optional[str] = None) -> AnswerEvaluation:
        """Оценка ответа пользователя с помощью OpenAI"""
        experts_section = f"\n\nМнения экспертов по теме (конспект):\n{multi_agent_notes}" if multi_agent_notes else ""
        rubric_text = build_rubric_text(question.category)
        rubric_section = f"\n\n{rubric_text}" if rubric_text else ""
        # Context7 (best-effort)
        docs_section = ""
        # Интеграция Context7 отключена

        system_prompt = f"""
        Ты эксперт по техническим собеседованиям. Оцени ответ кандидата на вопрос.
        
        Вопрос: {question.title}
        Содержание: {question.content}
        Правильный ответ: {question.correct_answer}
        Объяснение: {question.explanation or "Нет объяснения"}
        Уровень сложности: {question.level}
        Категория: {question.category}
        Максимальный балл: {question.points}
        {experts_section}{rubric_section}{docs_section}
        
        Ответ кандидата: {user_answer}
        Тип ответа: {answer_type}
        
        Оцени ответ по следующим критериям:
        1. Точность и полнота ответа (0-{question.points//2} баллов)
        2. Понимание концепций (0-{question.points//4} баллов)
        3. Качество объяснения (0-{question.points//4} баллов)
        
        Верни JSON в формате:
        {{
            "score": число_баллов,
            "feedback": "подробная обратная связь на русском языке",
            "is_correct": true/false,
            "strengths": ["сильные стороны ответа"],
            "improvements": ["что можно улучшить"]
        }}
        """

        for attempt in range(self._max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Оцени этот ответ: {user_answer}"}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                result = json.loads(response.choices[0].message.content)
                return AnswerEvaluation(
                    answer_id=0,
                    score=result["score"],
                    feedback=result["feedback"],
                    is_correct=result["is_correct"]
                )
            except Exception as e:
                logger.warning(f"OpenAI evaluate attempt {attempt+1} failed: {e}")
                if attempt == self._max_retries - 1:
                    logger.error(f"Ошибка при оценке ответа OpenAI: {e}")
                    return AnswerEvaluation(
                        answer_id=0,
                        score=0,
                        feedback="Произошла ошибка при оценке ответа. Попробуйте еще раз.",
                        is_correct=False
                    )
                await asyncio.sleep(0.5 * (2 ** attempt))
    
    async def transcribe_voice(self, voice_file_path: str) -> str:
        """Транскрипция голосового сообщения"""
        for attempt in range(self._max_retries):
            try:
                with open(voice_file_path, "rb") as audio_file:
                    transcript = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ru"
                    )
                    return transcript.text
            except Exception as e:
                logger.warning(f"OpenAI transcribe attempt {attempt+1} failed: {e}")
                if attempt == self._max_retries - 1:
                    logger.error(f"Ошибка при транскрипции OpenAI: {e}")
                    return ""
                await asyncio.sleep(0.5 * (2 ** attempt))


class GigaChatService(AIService):
    """Сервис для работы с GigaChat API"""
    
    def __init__(self):
        self.client_id = settings.gigachat_client_id
        self.client_secret = settings.gigachat_client_secret
        self.auth_url = settings.gigachat_auth_url
        self.api_url = settings.gigachat_api_url
        self.access_token = None
        self.token_expiry: Optional[datetime] = None
        self.session = aiohttp.ClientSession(timeout=ClientTimeout(total=20))
        self._max_retries = 3
    
    async def _get_access_token(self) -> str:
        """Получение access token для GigaChat"""
        # проверяем валидность токена
        if self.access_token and self.token_expiry and datetime.utcnow() < self.token_expiry:
            return self.access_token
        
        try:
            auth_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }
            
            async with self.session.post(self.auth_url, data=auth_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data["access_token"]
                    # expires_in в секундах, если нет — по умолчанию 10 минут
                    expires_in = int(token_data.get("expires_in", 600))
                    # небольшой запас 30 секунд
                    self.token_expiry = datetime.utcnow() + timedelta(seconds=max(expires_in - 30, 30))
                    return self.access_token
                else:
                    raise Exception(f"Ошибка авторизации GigaChat: {response.status}")
                    
        except Exception as e:
            logger.error(f"Ошибка при получении токена GigaChat: {e}")
            raise
    
    async def evaluate_answer(self, question: Question, user_answer: str,
                            answer_type: str = "text",
                            multi_agent_notes: Optional[str] = None) -> AnswerEvaluation:
        """Оценка ответа пользователя с помощью GigaChat"""
        
        experts_section = f"\n\nМнения экспертов по теме (конспект):\n{multi_agent_notes}" if multi_agent_notes else ""
        rubric_text = build_rubric_text(question.category)
        rubric_section = f"\n\n{rubric_text}" if rubric_text else ""
        system_prompt = f"""
        Ты эксперт по техническим собеседованиям. Оцени ответ кандидата на вопрос.
        
        Вопрос: {question.title}
        Содержание: {question.content}
        Правильный ответ: {question.correct_answer}
        Объяснение: {question.explanation or "Нет объяснения"}
        Уровень сложности: {question.level}
        Категория: {question.category}
        Максимальный балл: {question.points}
        {experts_section}{rubric_section}
        
        Ответ кандидата: {user_answer}
        Тип ответа: {answer_type}
        
        Оцени ответ по следующим критериям:
        1. Точность и полнота ответа (0-{question.points//2} баллов)
        2. Понимание концепций (0-{question.points//4} баллов)
        3. Качество объяснения (0-{question.points//4} баллов)
        
        Верни JSON в формате:
        {{
            "score": число_баллов,
            "feedback": "подробная обратная связь на русском языке",
            "is_correct": true/false,
            "strengths": ["сильные стороны ответа"],
            "improvements": ["что можно улучшить"]
        }}
        """
        
        for attempt in range(self._max_retries):
            try:
                access_token = await self._get_access_token()
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "GigaChat:latest",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Оцени этот ответ: {user_answer}"}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
                async with self.session.post(
                    f"{self.api_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 401:
                        # возможна просрочка токена — обновим и повторим
                        self.access_token = None
                        self.token_expiry = None
                        if attempt < self._max_retries - 1:
                            continue
                    if response.status in (429, 500, 502, 503, 504):
                        raise Exception(f"retryable status {response.status}")
                    if response.status == 200:
                        response_data = await response.json()
                        result = json.loads(response_data["choices"][0]["message"]["content"])
                        return AnswerEvaluation(
                            answer_id=0,
                            score=result["score"],
                            feedback=result["feedback"],
                            is_correct=result["is_correct"]
                        )
                    else:
                        raise Exception(f"Ошибка API GigaChat: {response.status}")
            except Exception as e:
                logger.warning(f"GigaChat evaluate attempt {attempt+1} failed: {e}")
                if attempt == self._max_retries - 1:
                    logger.error(f"Ошибка при оценке ответа GigaChat: {e}")
                    return AnswerEvaluation(
                        answer_id=0,
                        score=0,
                        feedback="Произошла ошибка при оценке ответа. Попробуйте еще раз.",
                        is_correct=False
                    )
                await asyncio.sleep(0.5 * (2 ** attempt))
    
    async def transcribe_voice(self, voice_file_path: str) -> str:
        """Транскрипция голосового сообщения через GigaChat"""
        # GigaChat пока не поддерживает транскрипцию аудио
        # Можно использовать внешний сервис или OpenAI только для транскрипции
        logger.warning("GigaChat не поддерживает транскрипцию аудио. Используйте OpenAI для транскрипции.")
        return ""
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()


def get_ai_service() -> AIService:
    """Фабрика для создания AI сервиса"""
    if settings.ai_provider.lower() == "gigachat":
        return GigaChatService()
    else:
        return OpenAIService()


class QuestionService:
    """Сервис для работы с вопросами"""
    
    @staticmethod
    async def get_question_for_user(user_id: int, level: str, category: str) -> Optional[Question]:
        """Получение вопроса для пользователя"""
        # Получаем пользователя
        user = await database.get_user_by_telegram_id(user_id)
        if not user:
            return None
        
        # Получаем случайный вопрос
        question = await database.get_random_question(level, category)
        if question:
            # Обновляем текущий вопрос пользователя
            await database.update_user(user_id, current_question_id=question.id)
        
        return question
    
    @staticmethod
    async def get_question_by_id(question_id: int) -> Optional[Question]:
        """Получение вопроса по ID"""
        return await database.get_question_by_id(question_id)


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    async def get_or_create_user(telegram_id: int, username: str = None, 
                                first_name: str = None, last_name: str = None) -> User:
        """Получение или создание пользователя"""
        user = await database.get_user_by_telegram_id(telegram_id)
        if not user:
            user = await database.create_user(telegram_id, username, first_name, last_name)
        return user
    
    @staticmethod
    async def update_user_level(telegram_id: int, level: str) -> Optional[User]:
        """Обновление уровня пользователя"""
        return await database.update_user(telegram_id, level=level)
    
    @staticmethod
    async def update_user_category(telegram_id: int, category: str) -> Optional[User]:
        """Обновление категории пользователя"""
        return await database.update_user(telegram_id, category=category)
    
    @staticmethod
    async def get_user_stats(telegram_id: int) -> UserStats:
        """Получение статистики пользователя"""
        user = await database.get_user_by_telegram_id(telegram_id)
        if not user:
            return UserStats(user_id=0)
        
        stats_data = await database.get_user_stats(user.id)
        return UserStats(**stats_data)


class AnswerService:
    """Сервис для работы с ответами"""
    
    def __init__(self):
        self.ai_service = get_ai_service()
        # Для транскрипции голоса всегда используем OpenAI, так как GigaChat не поддерживает
        self.openai_service = OpenAIService() if settings.ai_provider.lower() == "gigachat" else self.ai_service
    
    async def process_text_answer(self, user_id: int, question_id: int, 
                                 answer_text: str) -> Tuple[Answer, AnswerEvaluation]:
        """Обработка текстового ответа"""
        # Получаем пользователя
        user = await database.get_user_by_telegram_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        # Получаем вопрос
        question = await database.get_question_by_id(question_id)
        if not question:
            raise ValueError("Вопрос не найден")
        
        # Создаем ответ
        answer = await database.create_answer(
            user_id=user.id,
            question_id=question_id,
            answer_text=answer_text,
            answer_type="text"
        )
        
        # Мультиагентные заметки для выбранных категорий (MVP: system_design)
        expert_notes = await InterviewService.prepare_expert_notes(
            category=question.category,
            user_id=user.telegram_id,
            level=user.level or "",
            topic=question.title
        )

        # Оцениваем ответ с учетом expert notes (если есть)
        evaluation = await self.ai_service.evaluate_answer(
            question,
            answer_text,
            multi_agent_notes=expert_notes or None,
        )
        evaluation.answer_id = answer.id
        
        # Обновляем оценку в базе
        await database.update_answer_score(answer.id, evaluation.score, evaluation.feedback)
        
        # Обновляем статистику пользователя
        await database.update_user(
            user_id,
            score=user.score + evaluation.score,
            questions_answered=user.questions_answered + 1
        )
        
        return answer, evaluation
    
    async def process_voice_answer(self, user_id: int, question_id: int, 
                                  voice_file_path: str, voice_file_id: str) -> Tuple[Answer, AnswerEvaluation]:
        """Обработка голосового ответа"""
        # Транскрибируем голос
        answer_text = await self.openai_service.transcribe_voice(voice_file_path)
        
        if not answer_text:
            raise ValueError("Не удалось распознать голосовое сообщение")
        
        # Получаем пользователя
        user = await database.get_user_by_telegram_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        # Получаем вопрос
        question = await database.get_question_by_id(question_id)
        if not question:
            raise ValueError("Вопрос не найден")
        
        # Создаем ответ
        answer = await database.create_answer(
            user_id=user.id,
            question_id=question_id,
            answer_text=answer_text,
            answer_type="voice",
            voice_file_id=voice_file_id
        )
        
        # Мультиагентные заметки
        expert_notes = await InterviewService.prepare_expert_notes(
            category=question.category,
            user_id=user.telegram_id,
            level=user.level or "",
            topic=question.title
        )

        # Оцениваем ответ с учетом expert notes (если есть)
        evaluation = await self.ai_service.evaluate_answer(
            question,
            answer_text,
            "voice",
            multi_agent_notes=expert_notes or None,
        )
        evaluation.answer_id = answer.id
        
        # Обновляем оценку в базе
        await database.update_answer_score(answer.id, evaluation.score, evaluation.feedback)
        
        # Обновляем статистику пользователя
        await database.update_user(
            user_id,
            score=user.score + evaluation.score,
            questions_answered=user.questions_answered + 1
        )
        
        return answer, evaluation


class VoiceService:
    """Сервис для работы с голосовыми сообщениями"""
    
    @staticmethod
    async def download_voice_file(file_id: str, bot_token: str, save_path: str) -> bool:
        """Скачивание голосового файла из Telegram"""
        try:
            # Получаем информацию о файле
            async with aiohttp.ClientSession() as session:
                # Получаем file_path
                file_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
                async with session.get(file_url) as response:
                    file_info = await response.json()
                    if not file_info.get("ok"):
                        return False
                    
                    file_path = file_info["result"]["file_path"]
                
                # Скачиваем файл
                download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                async with session.get(download_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(save_path, 'wb') as f:
                            await f.write(await response.read())
                        return True
                    else:
                        return False
                        
        except Exception as e:
            logger.error(f"Ошибка при скачивании файла: {e}")
            return False
    
    @staticmethod
    async def convert_ogg_to_wav(ogg_path: str, wav_path: str) -> bool:
        """Конвертация OGG в WAV для лучшей совместимости"""
        try:
            audio = AudioSegment.from_ogg(ogg_path)
            audio.export(wav_path, format="wav")
            return True
        except Exception as e:
            logger.error(f"Ошибка при конвертации аудио: {e}")
            return False 