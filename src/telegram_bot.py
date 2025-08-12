import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

from .config import settings, AppConstants
from .container import (
    get_user_app_service,
    get_question_app_service,
    get_answer_app_service,
)
from .models import User, Question

logger = logging.getLogger(__name__)


class InterviewBot:
    """Telegram бот для подготовки к техническим собеседованиям"""
    
    def __init__(self):
        self.application = Application.builder().token(settings.telegram_bot_token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        
        # Обработка callback query (кнопки)
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Обработка текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        # Обработка голосовых сообщений
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        
        # Обработка ошибок
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user = update.effective_user
        
        # Создаем или получаем пользователя через app-layer
        users = get_user_app_service()
        await users.get_or_create(user.id, user.username, user.first_name, user.last_name)
        
        welcome_text = f"""
👋 Привет, {user.first_name or user.username or 'пользователь'}!

Я бот для подготовки к техническим собеседованиям. 

🎯 Что я умею:
• Задавать вопросы по разным уровням сложности
• Оценивать ваши ответы (текст или голос)
• Давать подробную обратную связь
• Отслеживать ваш прогресс

🚀 Начнем! Выберите ваш уровень:
        """
        
        keyboard = [
            [InlineKeyboardButton("👶 Junior", callback_data="level_junior")],
            [InlineKeyboardButton("👨‍💻 Middle", callback_data="level_middle")],
            [InlineKeyboardButton("👨‍💼 Senior", callback_data="level_senior")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        help_text = """
📚 Справка по использованию бота:

🔹 /start - Начать работу с ботом
🔹 /help - Показать эту справку
🔹 /stats - Показать вашу статистику
🔹 /settings - Настройки профиля

📝 Как отвечать на вопросы:
• Текстом - просто напишите ответ
• Голосом - отправьте голосовое сообщение

🎯 Уровни сложности:
• Junior - базовые концепции
• Middle - углубленные знания
• Senior - архитектурные решения

📊 Категории вопросов (backend-фокус):
• System Design - проектирование систем
• Algorithms - алгоритмы и структуры данных
• Databases - базы данных
• Networking - сетевые технологии
• Security - безопасность
• Backend - бэкенд разработка
        """
        
        await update.message.reply_text(help_text)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /stats"""
        user_id = update.effective_user.id
        
        try:
            stats = await UserService.get_user_stats(user_id)
            
            if stats.user_id == 0:
                await update.message.reply_text("❌ Статистика не найдена. Используйте /start для начала работы.")
                return
            
            stats_text = f"""
📊 Ваша статистика:

🎯 Уровень: {stats.level or 'Не выбран'}
📂 Категория: {stats.category or 'Не выбрана'}
🏆 Общий счет: {stats.total_score}
❓ Отвечено вопросов: {stats.questions_answered}
📈 Средний балл: {stats.average_score:.1f}
🕐 Последняя активность: {stats.last_activity.strftime('%d.%m.%Y %H:%M') if stats.last_activity else 'Нет данных'}
            """
            
            await update.message.reply_text(stats_text)
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            await update.message.reply_text("❌ Ошибка при получении статистики")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /settings"""
        user_id = update.effective_user.id
        
        try:
            users = get_user_app_service()
            user = await users.get_or_create(user_id, None, None, None)
            
            settings_text = f"""
⚙️ Настройки профиля:

👤 Пользователь: {user.first_name or user.username or 'Не указано'}
🎯 Уровень: {user.level or 'Не выбран'}
📂 Категория: {user.category or 'Не выбрана'}

Выберите, что хотите изменить:
            """
            
            keyboard = [
                [InlineKeyboardButton("🎯 Изменить уровень", callback_data="settings_level")],
                [InlineKeyboardButton("📂 Изменить категорию", callback_data="settings_category")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(settings_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка при получении настроек: {e}")
            await update.message.reply_text("❌ Ошибка при получении настроек")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback query от кнопок"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        try:
            if data.startswith("level_"):
                level = data.split("_")[1]
                await self.handle_level_selection(query, level)
                
            elif data.startswith("category_"):
                category = data.split("_")[1]
                await self.handle_category_selection(query, category)
                
            elif data == "settings_level":
                await self.show_level_selection(query)
                
            elif data == "settings_category":
                await self.show_category_selection(query)
                
            elif data == "get_question":
                await self.get_question_for_user(query, user_id)
                
            elif data == "skip_question":
                await self.skip_question(query, user_id)
                
        except Exception as e:
            logger.error(f"Ошибка при обработке callback: {e}")
            await query.edit_message_text("❌ Произошла ошибка. Попробуйте еще раз.")
    
    async def handle_level_selection(self, query, level: str):
        """Обработка выбора уровня"""
        user_id = query.from_user.id
        
        # Обновляем уровень пользователя
        users = get_user_app_service()
        await users.update_level(user_id, level)
        
        # Показываем выбор категории
        level_name = AppConstants.LEVELS.get(level, level)
        text = f"✅ Выбран уровень: {level_name}\n\nТеперь выберите категорию вопросов:"
        
        keyboard = []
        for key, value in AppConstants.CATEGORIES.items():
            keyboard.append([InlineKeyboardButton(value, callback_data=f"category_{key}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def handle_category_selection(self, query, category: str):
        """Обработка выбора категории"""
        user_id = query.from_user.id
        
        # Обновляем категорию пользователя
        users = get_user_app_service()
        await users.update_category(user_id, category)
        
        # Показываем готовность к вопросам
        category_name = AppConstants.CATEGORIES.get(category, category)
        text = f"✅ Выбрана категория: {category_name}\n\nГотовы к вопросам! Нажмите кнопку ниже:"
        
        keyboard = [[InlineKeyboardButton("🎯 Получить вопрос", callback_data="get_question")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def show_level_selection(self, query):
        """Показать выбор уровня для настроек"""
        text = "Выберите новый уровень:"
        
        keyboard = [
            [InlineKeyboardButton("👶 Junior", callback_data="level_junior")],
            [InlineKeyboardButton("👨‍💻 Middle", callback_data="level_middle")],
            [InlineKeyboardButton("👨‍💼 Senior", callback_data="level_senior")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def show_category_selection(self, query):
        """Показать выбор категории для настроек"""
        text = "Выберите новую категорию:"
        
        keyboard = []
        for key, value in AppConstants.CATEGORIES.items():
            keyboard.append([InlineKeyboardButton(value, callback_data=f"category_{key}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def get_question_for_user(self, query, user_id: int):
        """Получение вопроса для пользователя"""
        try:
            users = get_user_app_service()
            user = await users.get_or_create(user_id, None, None, None)
            
            if not user.level or not user.category:
                await query.edit_message_text(
                    "❌ Сначала выберите уровень и категорию. Используйте /start"
                )
                return
            
            # Получаем вопрос
            qs = get_question_app_service()
            question = await qs.random_for_user(user_id, user.level, user.category)
            
            if not question:
                await query.edit_message_text(
                    f"❌ Вопросы для уровня {user.level} и категории {user.category} не найдены"
                )
                return
            
            # Формируем сообщение с вопросом
            question_text = f"""
🎯 Вопрос #{question.id}

📝 {question.title}

📄 {question.content}

💡 Подсказки: {', '.join(question.hints) if question.hints else 'Нет подсказок'}
🏆 Максимальный балл: {question.points}

💬 Отправьте ваш ответ текстом или голосовым сообщением.
            """
            
            keyboard = [[InlineKeyboardButton("⏭️ Пропустить вопрос", callback_data="skip_question")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(question_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка при получении вопроса: {e}")
            await query.edit_message_text("❌ Ошибка при получении вопроса")
    
    async def skip_question(self, query, user_id: int):
        """Пропуск вопроса"""
        try:
            users = get_user_app_service()
            user = await users.get_or_create(user_id, None, None, None)
            
            # Получаем новый вопрос
            qs = get_question_app_service()
            question = await qs.random_for_user(user_id, user.level, user.category)
            
            if not question:
                await query.edit_message_text(
                    f"❌ Больше вопросов для уровня {user.level} и категории {user.category} не найдено"
                )
                return
            
            # Показываем новый вопрос
            await self.get_question_for_user(query, user_id)
            
        except Exception as e:
            logger.error(f"Ошибка при пропуске вопроса: {e}")
            await query.edit_message_text("❌ Ошибка при пропуске вопроса")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text
        
        try:
            users = get_user_app_service()
            user = await users.get_or_create(user_id, None, None, None)
            
            if not user.current_question_id:
                await update.message.reply_text(
                    "❌ У вас нет активного вопроса. Используйте /start для начала работы."
                )
                return
            
            # Обрабатываем текстовый ответ
            answers = get_answer_app_service()
            # Для отображения баллов получим вопрос
            qs = get_question_app_service()
            question = await qs.get(user.current_question_id)
            answer, evaluation = await answers.answer_text(user_id, user.current_question_id, text)
            
            # Формируем ответ с оценкой
            points = question.points if question else 0
            response_text = f"""
📊 Результат оценки:

🏆 Получено баллов: {evaluation.score}/{points}
✅ Правильность: {'Да' if evaluation.is_correct else 'Нет'}

💬 Обратная связь:
{evaluation.feedback}

🎯 Хотите еще один вопрос?
            """
            
            keyboard = [[InlineKeyboardButton("🎯 Следующий вопрос", callback_data="get_question")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке текстового ответа: {e}")
            await update.message.reply_text("❌ Ошибка при обработке ответа")
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка голосовых сообщений"""
        user_id = update.effective_user.id
        voice = update.message.voice
        
        try:
            users = get_user_app_service()
            user = await users.get_or_create(user_id, None, None, None)
            
            if not user.current_question_id:
                await update.message.reply_text(
                    "❌ У вас нет активного вопроса. Используйте /start для начала работы."
                )
                return
            
            # Отправляем сообщение о обработке
            processing_msg = await update.message.reply_text("🎤 Обрабатываю голосовое сообщение...")
            
            # Скачиваем и обрабатываем голосовое сообщение
            answers = get_answer_app_service()
            qs = get_question_app_service()
            question = await qs.get(user.current_question_id)
            answer, evaluation = await answers.answer_voice(
                user_id, user.current_question_id, voice.file_id, settings.telegram_bot_token
            )
            
            # Формируем ответ с оценкой
            points = question.points if question else 0
            response_text = f"""
📊 Результат оценки:

🎤 Распознанный текст: "{answer.answer_text}"

🏆 Получено баллов: {evaluation.score}/{points}
✅ Правильность: {'Да' if evaluation.is_correct else 'Нет'}

💬 Обратная связь:
{evaluation.feedback}

🎯 Хотите еще один вопрос?
            """
            
            keyboard = [[InlineKeyboardButton("🎯 Следующий вопрос", callback_data="get_question")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.edit_text(response_text, reply_markup=reply_markup)
            
            # Файлы очищаются на уровне AnswerAppService через VoiceStorage
            
        except Exception as e:
            logger.error(f"Ошибка при обработке голосового ответа: {e}")
            await update.message.reply_text("❌ Ошибка при обработке голосового ответа")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ошибок"""
        logger.error(f"Ошибка в боте: {context.error}")
        
        if update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуйте еще раз или используйте /help для справки."
            )
    
    async def run(self):
        """Запуск бота"""
        logger.info("Запуск Telegram бота...")
        await self.application.run_polling()


# Создание экземпляра бота
bot = InterviewBot() 