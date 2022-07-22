import logging
import os
import redis
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from dotenv import load_dotenv
from random import choice, randint
from quiz_tools import get_questions

logger = logging.getLogger(__name__)


def reply(vk_api, user_id, text, keyboard=False):
    keyboard = keyboard.get_keyboard() if keyboard else None
    vk_api.messages.send(
        user_id=user_id,
        message=text,
        keyboard=keyboard,
        random_id=randint(1, 1000000)
    )


def start(event, vk_api, keyboard):
    reply(vk_api, event.obj['message']['from_id'],
          'Привет. Я хочу сыграть с тобой в игру!', keyboard)


def handle_new_question_request(event, vk_api, questions, redis_handler):
    user_id = event.obj['message']['from_id']
    question, answer = choice(list(questions.items()))
    redis_handler.set(user_id, question)
    reply(vk_api, user_id, question)


def handle_solution_attempt(event, vk_api, questions, redis_handler, keyboard):
    user_id = event.obj['message']['from_id']
    question = redis_handler.get(user_id)
    answer = questions[question]
    if event.obj['message']['text'].strip().lower() == answer.lower():
        reply(vk_api, user_id,
              'Поздравляю! Для продолжения нажми «Новый вопрос»', keyboard)
    else:
        reply(vk_api, user_id, 'Неправильно. Попробуешь ещё раз?', keyboard)


def give_up(event, vk_api, questions, redis_handler):
    user_id = event.obj['message']['from_id']
    question = redis_handler.get(user_id)
    answer = questions[question]
    reply(vk_api, user_id, f'Правильный ответ: {answer}')

    question, answer = choice(list(questions.items()))
    redis_handler.set(user_id, question)
    reply(vk_api, user_id, question)


def main():
    load_dotenv()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    redis_handler = redis.Redis(
        host='redis-17040.c293.eu-central-1-1.ec2.cloud.redislabs.com',
        port=17040,
        username='default',
        password='Vu2FxbRBS359ZllgukdN8QL9mW6S5KpD',
        decode_responses=True
    )

    questions = get_questions()

    vk_session = vk_api.VkApi(token=os.getenv('VK_TOKEN'))
    vk_session_api = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, os.getenv('VK_GROUP_ID'))

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)

    game_started = False
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            message_text = event.obj['message']['text']
            if message_text == 'Новый вопрос':
                handle_new_question_request(event, vk_session_api, questions,
                                            redis_handler)
                game_started = True
            elif message_text == 'Сдаться':
                give_up(event, vk_session_api, questions, redis_handler)
            elif game_started:
                handle_solution_attempt(event, vk_session_api, questions,
                                        redis_handler, keyboard)
            else:
                start(event, vk_session_api, keyboard)


if __name__ == '__main__':
    main()
