Mountain Passes API
REST API для системы управления информацией о горных перевалах.
Проект выполнен в рамках спринта: реализация метода POST /submitData для приёма данных от мобильного приложения.

Описание проекта
Турист с помощью мобильного приложения отправляет информацию о перевале:

координаты и высоту;

название объекта;

несколько фотографий;

данные о пользователе (ФИО, email, телефон).

Мобильное приложение вызывает метод POST /submitData, который:

валидирует входной JSON;

записывает данные в PostgreSQL (пользователь, перевал, уровни сложности, фото);

возвращает JSON‑ответ с кодом статуса, сообщением и id созданного перевала.

Технологии
Python 3.11+

FastAPI

PostgreSQL

psycopg2‑binary

Pydantic

python‑dotenv

Pillow

Зависимости перечислены в requirements.txt.

Установка и запуск
1. Клонирование репозитория
bash
git clone https://github.com/ВАШ_ЛОГИН/ВАШ_РЕПОЗИТОРИЙ.git
cd ВАШ_РЕПОЗИТОРИЙ
2. Виртуальное окружение (рекомендовано)
bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
# или
.venv\Scripts\activate         # Windows
3. Установка зависимостей
bash
pip install -r requirements.txt
4. Настройка переменных окружения
Создайте файл .env в корне проекта на основе примера:

bash
cp .env.example .env
И отредактируйте .env, указав свои настройки PostgreSQL:

text
FSTR_DB_HOST=localhost
FSTR_DB_PORT=5432
FSTR_DB_LOGIN=postgres
FSTR_DB_PASS=your_password
FSTR_DB_NAME=mountain_passes
5. Подготовка базы данных
Создайте БД в PostgreSQL:

sql
CREATE DATABASE mountain_passes;
Создайте таблицы (примерно, в соответствии со схемой проекта):

users — пользователи (email, телефон, ФИО и т.д.);

passes — перевалы (название, координаты, высота, статус модерации и т.д.);

difficulty_levels — уровни сложности по сезонам;

images — фотографии.

(Схему можно оформить отдельным SQL‑скриптом и приложить в репозиторий.)

6. Запуск приложения
bash
uvicorn app.main:app --reload
По умолчанию приложение будет доступно по адресу:

Swagger‑документация: http://localhost:8000/docs

Корневой эндпоинт: http://localhost:8000/

Проверка здоровья: http://localhost:8000/health

Эндпоинты
POST /submitData
Принимает JSON с информацией о перевале и возвращает результат обработки.

Пример тела запроса:

json
{
  "beauty_title": "пер. ",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2021-09-22 13:18:13",
  "user": {
    "email": "qwerty@mail.ru",
    "fam": "Пупкин",
    "name": "Василий",
    "otc": "Иванович",
    "phone": "+7 555 55 55"
  },
  "coords": {
    "latitude": "45.3842",
    "longitude": "7.1525",
    "height": "1200"
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    { "data": "<картинка1>", "title": "Седловина" },
    { "data": "<картинка2>", "title": "Подъём" }
  ]
}
Пример успешного ответа:

json
{
  "status": 200,
  "message": null,
  "id": 42
}
Примеры ошибок:

json
{ "status": 400, "message": "Не хватает обязательных полей", "id": null }
{ "status": 500, "message": "Ошибка подключения к базе данных", "id": null }
Структура проекта
text
project/
├── app/
│   ├── __init__.py
│   ├── main.py         # Точка входа FastAPI, REST эндпоинты
│   ├── models.py       # Pydantic‑модели для валидации JSON
│   └── database.py     # Класс Database: работа с PostgreSQL
├── .env.example        # Пример настроек окружения
├── requirements.txt    # Зависимости
└── README.md
Работа с базой данных
Класс Database отвечает за:

подключение к PostgreSQL с использованием переменных окружения;

создание/поиск пользователя;

добавление перевала с начальным статусом new;

сохранение уровней сложности (winter, spring, summer, autumn);

сохранение фотографий (данные в бинарном виде).

Поле status в таблице перевалов может принимать значения:

new — новый объект;

pending — модерация в процессе;

accepted — модерация завершена, данные приняты;

rejected — модерация завершена, данные отклонены.

Работа с Git
Проект ведётся с использованием Git:

основная ветка: master (или main);

для реализации метода submitData используется отдельная ветка submitData;

работа над фичей ведётся через последовательность осмысленных коммитов;

после завершения ветка submitData сливается в master.

Контакты
Автор: ealukina
Если есть вопросы или предложения — пишите
