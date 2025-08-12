from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .config import settings

# Создаем базовый класс для моделей
Base = declarative_base()


class User(Base):
    """Модель пользователя в базе данных"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    level = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    current_question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    score = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Отношения
    answers = relationship("Answer", back_populates="user")
    current_question = relationship("Question", foreign_keys=[current_question_id])


class Question(Base):
    """Модель вопроса в базе данных"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    level = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    question_type = Column(String(50), nullable=False)
    points = Column(Integer, default=10)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    hints = Column(JSON, nullable=True)  # Список подсказок
    tags = Column(JSON, nullable=True)   # Список тегов
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Отношения
    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    """Модель ответа в базе данных"""
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    answer_type = Column(String(20), nullable=False)  # text или voice
    score = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    voice_file_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    user = relationship("User", back_populates="answers")
    question = relationship("Question", back_populates="answers")


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
    
    async def connect(self):
        """Подключение к базе данных"""
        # Конвертируем URL для async
        if settings.database_url.startswith("sqlite"):
            async_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")
        else:
            async_url = settings.database_url
        
        self.engine = create_async_engine(
            async_url,
            echo=False,
            pool_pre_ping=True
        )
        
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def disconnect(self):
        """Отключение от базы данных"""
        if self.engine:
            await self.engine.dispose()
    
    async def create_tables(self):
        """Создание таблиц"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    def get_session(self) -> AsyncSession:
        """Получение сессии базы данных (async session factory)"""
        if not self.session_maker:
            raise RuntimeError("База данных не подключена")
        return self.session_maker()
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по Telegram ID"""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM users WHERE telegram_id = :telegram_id"),
                {"telegram_id": telegram_id},
            )
            return result.scalar_one_or_none()
    
    async def create_user(self, telegram_id: int, username: str = None, 
                         first_name: str = None, last_name: str = None) -> User:
        """Создание нового пользователя"""
        async with self.get_session() as session:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    async def update_user(self, telegram_id: int, **kwargs) -> Optional[User]:
        """Обновление пользователя"""
        async with self.get_session() as session:
            result = await session.execute(
                text(
                    "UPDATE users SET updated_at = :updated_at, "
                    + ", ".join([f"{k} = :{k}" for k in kwargs.keys()])
                    + " WHERE telegram_id = :telegram_id"
                ),
                {"telegram_id": telegram_id, "updated_at": datetime.now(), **kwargs},
            )
            await session.commit()
            
            if result.rowcount > 0:
                return await self.get_user_by_telegram_id(telegram_id)
            return None
    
    async def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """Получение вопроса по ID"""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM questions WHERE id = :question_id"),
                {"question_id": question_id},
            )
            return result.scalar_one_or_none()
    
    async def get_random_question(self, level: str, category: str, 
                                 exclude_ids: List[int] = None) -> Optional[Question]:
        """Получение случайного вопроса"""
        async with self.get_session() as session:
            query = (
                "SELECT * FROM questions WHERE level = :level AND category = :category "
                "ORDER BY RANDOM() LIMIT 1"
            )
            params = {"level": level, "category": category}
            result = await session.execute(text(query), params)
            return result.scalar_one_or_none()
    
    async def create_answer(self, user_id: int, question_id: int, 
                           answer_text: str, answer_type: str, 
                           voice_file_id: str = None) -> Answer:
        """Создание ответа"""
        async with self.get_session() as session:
            answer = Answer(
                user_id=user_id,
                question_id=question_id,
                answer_text=answer_text,
                answer_type=answer_type,
                voice_file_id=voice_file_id
            )
            session.add(answer)
            await session.commit()
            await session.refresh(answer)
            return answer
    
    async def update_answer_score(self, answer_id: int, score: int, 
                                 feedback: str) -> Optional[Answer]:
        """Обновление оценки ответа"""
        async with self.get_session() as session:
            result = await session.execute(
                text("UPDATE answers SET score = :score, feedback = :feedback WHERE id = :answer_id"),
                {"answer_id": answer_id, "score": score, "feedback": feedback},
            )
            await session.commit()
            
            if result.rowcount > 0:
                result = await session.execute(
                    text("SELECT * FROM answers WHERE id = :answer_id"),
                    {"answer_id": answer_id},
                )
                return result.scalar_one_or_none()
            return None
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики пользователя"""
        async with self.get_session() as session:
            result = await session.execute(
                text(
                    """
                SELECT 
                    u.score as total_score,
                    u.questions_answered,
                    u.level,
                    u.category,
                    u.updated_at as last_activity,
                    CASE 
                        WHEN u.questions_answered > 0 
                        THEN CAST(u.score AS FLOAT) / u.questions_answered 
                        ELSE 0 
                    END as average_score
                FROM users u 
                WHERE u.id = :user_id
            """
                ),
                {"user_id": user_id},
            )
            
            row = result.fetchone()
            if row:
                return {
                    "user_id": user_id,
                    "total_score": row.total_score,
                    "questions_answered": row.questions_answered,
                    "average_score": row.average_score,
                    "level": row.level,
                    "category": row.category,
                    "last_activity": row.last_activity
                }
            return {}


# Глобальный экземпляр базы данных
database = Database() 