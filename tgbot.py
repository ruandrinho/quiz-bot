import logging
import os
import redis
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes,\
    MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv
from random import choice
from functools import partial
from quiz_tools import get_questions

logger = logging.getLogger(__name__)

NEW_QUESTION, ANSWER = range(2)
REPLY_KEYBOARD = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]


async def reply(update: Update, text, keyboard=False):
    reply_markup = None
    if keyboard:
        reply_markup = ReplyKeyboardMarkup(
            REPLY_KEYBOARD,
            one_time_keyboard=True
        )
    await update.message.reply_text(text, reply_markup=reply_markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE,
                reply_markup=None):
    await update.message.reply_text(
        'Привет. Я хочу сыграть с тобой в игру!',
        reply_markup=reply_markup
    )
    return NEW_QUESTION


async def handle_new_question_request(update: Update,
                                      context: ContextTypes.DEFAULT_TYPE,
                                      questions: dict, redis_handler,
                                      reply_markup=None):
    user = update.message.from_user
    question, answer = choice(list(questions.items()))
    redis_handler.set(user.id, question)
    await update.message.reply_text(question, reply_markup=reply_markup)
    return ANSWER


async def handle_solution_attempt(update: Update,
                                  context: ContextTypes.DEFAULT_TYPE,
                                  questions: dict, redis_handler,
                                  reply_markup=None):
    user = update.message.from_user
    question = redis_handler.get(user.id)
    answer = questions[question]
    if update.message.text.strip().lower() == answer.lower():
        await update.message.reply_text(
            'Поздравляю! Для продолжения нажми «Новый вопрос»',
            reply_markup=reply_markup
        )
        return NEW_QUESTION
    else:
        await update.message.reply_text(
            'Неправильно. Попробуешь ещё раз?',
            reply_markup=reply_markup
        )
        return ANSWER


async def give_up(update: Update, context: ContextTypes.DEFAULT_TYPE,
                  questions: dict, redis_handler, reply_markup=None):
    user = update.message.from_user
    question = redis_handler.get(user.id)
    answer = questions[question]
    await update.message.reply_text(
        f'Правильный ответ: {answer}',
        reply_markup=reply_markup
    )

    question, answer = choice(list(questions.items()))
    redis_handler.set(user.id, question)
    await update.message.reply_text(question, reply_markup=reply_markup)
    return ANSWER


def main():
    load_dotenv()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    redis_handler = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        username=os.getenv('REDIS_USERNAMET'),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )

    questions = get_questions(os.getenv('QUESTIONS_FOLDER'))

    token = os.getenv('TELEGRAM_TOKEN')
    application = Application.builder().token(token).build()

    reply_markup = ReplyKeyboardMarkup(
        REPLY_KEYBOARD,
        one_time_keyboard=True
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(
            'start',
            partial(
                start,
                reply_markup=reply_markup
            )
        )],
        states={
            NEW_QUESTION: [MessageHandler(
                filters.Regex('^(Новый вопрос)$'),
                partial(
                    handle_new_question_request,
                    questions=questions,
                    redis_handler=redis_handler
                )
            )],
            ANSWER: [MessageHandler(
                filters.TEXT & ~filters.COMMAND &
                ~filters.Regex('^(Сдаться)$'),
                partial(
                    handle_solution_attempt,
                    questions=questions,
                    redis_handler=redis_handler,
                    reply_markup=reply_markup
                )
            )]
        },
        fallbacks=[
            MessageHandler(
                filters.Regex('^(Сдаться)$'),
                partial(
                    give_up,
                    questions=questions,
                    redis_handler=redis_handler
                )
            )
        ]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
