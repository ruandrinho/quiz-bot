# quiz-bot
 
Бот викторины исторического музея

Рабочие версии: [telegram](https://t.me/quiz_andrinho_bot), [vk](https://vk.com/club214480939) (нажмите «Написать сообщение»)

## Как установить

Клонируйте репозиторий или скачайте архив и распакуйте.

Создайте телеграм-бота, группу VK и базу данных Redis.

Создайте файл окружения `.env` и заполните необходимым данными:
```
TELEGRAM_BOT_TOKEN=
VK_GROUP_ID=
VK_TOKEN=
REDIS_HOST=
REDIS_PORT=
REDIS_USERNAME=
REDIS_PASSWORD=
QUESTIONS_FOLDER=questions
```

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

## Запуск скриптов

```
python vkbot.py
python tgbot.py
```

## Деплой на Heroku

Скрипт полностью готов к деплою. Сделайте форк репозитория, создайте новое приложение на Heroku, после чего в разделе Settings:
1. Подключите приложение к своему репозиторию
2. Задайте те же Config Vars, что и для файла .env
3. Нажмите на кнопку Deploy Branch

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
