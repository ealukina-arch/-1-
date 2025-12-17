"""
Класс для работы с базой данных PostgreSQL.
Это промежуточный слой между REST API и БД.
"""

import os
import base64
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 мегабайт


class Database:
    """
    Класс для подключения и работы с PostgreSQL.

    Все параметры подключения берутся из переменных окружения:
    - FSTR_DB_HOST: адрес сервера БД
    - FSTR_DB_PORT: порт
    - FSTR_DB_LOGIN: логин
    - FSTR_DB_PASS: пароль
    - FSTR_DB_NAME: название БД
    """

    def __init__(self):
        """
        Инициализация подключения к БД.
        Все параметры берутся из переменных окружения.
        """
        self.host = os.getenv('FSTR_DB_HOST', 'localhost')
        self.port = os.getenv('FSTR_DB_PORT', '5432')
        self.user = os.getenv('FSTR_DB_LOGIN', 'postgres')
        self.password = os.getenv('FSTR_DB_PASS', 'postgres')
        self.database = os.getenv('FSTR_DB_NAME', 'mountain_passes')
        self.connection = None

    def connect(self) -> bool:
        """
        Подключиться к БД.
        Возвращает True, если успешно, False если ошибка.
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        """Отключиться от БД."""
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: tuple = None) -> bool:
        """
        Выполнить SQL запрос (INSERT, UPDATE, DELETE).

        Args:
            query: SQL запрос
            params: параметры для запроса

        Returns:
            True если успешно, False если ошибка
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            cursor.close()
            return True
        except psycopg2.Error as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            return False

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Получить одну строку из БД.

        Args:
            query: SQL запрос
            params: параметры для запроса

        Returns:
            Словарь с данными или None
        """
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        except psycopg2.Error as e:
            logger.error(f"Ошибка при получении данных: {e}")
            return None

    def fetch_all(self, query: str, params: tuple = None) -> list:
        """
        Получить все строки из БД.

        Args:
            query: SQL запрос
            params: параметры для запроса

        Returns:
            Список словарей с данными
        """
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result if result else []
        except psycopg2.Error as e:
            logger.error(f"Ошибка при получении данных: {e}")
            return []

    def get_last_insert_id(self) -> Optional[int]:
        """
        Получить ID последней вставленной записи.

        Returns:
            ID или None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT lastval()")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Ошибка при получении ID: {e}")
            return None

    def create_user(self, email: str, phone: str, fam: str, name: str, otc: str) -> Optional[int]:
        """
        Создать нового пользователя в БД.

        Args:
            email: email пользователя
            phone: телефон
            fam: фамилия
            name: имя
            otc: отчество

        Returns:
            ID созданного пользователя или None если ошибка
        """
        query = """
            INSERT INTO users (email, phone, fam, name, otc)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (email, phone, fam, name, otc))
            user_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            return user_id
        except psycopg2.IntegrityError:
            # Пользователь с таким email уже существует
            self.connection.rollback()
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            self.connection.rollback()
            return None

    def create_pass(self, beauty_title: str, title: str, other_titles: str,
                    connect: str, add_time: str, user_id: int,
                    latitude: float, longitude: float, height: int) -> Optional[int]:
        """
        Создать новый перевал в БД.

        Args:
            beauty_title: красивое название
            title: название перевала
            other_titles: другие названия
            connect: что соединяет
            add_time: время добавления
            user_id: ID пользователя
            latitude: широта
            longitude: долгота
            height: высота

        Returns:
            ID созданного перевала или None если ошибка
        """
        query = """
            INSERT INTO passes (beauty_title, title, other_titles, connect, 
                              add_time, user_id, latitude, longitude, height, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'new')
            RETURNING id;
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (beauty_title, title, other_titles, connect,
                                   add_time, user_id, latitude, longitude, height))
            pass_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            return pass_id
        except psycopg2.Error as e:
            logger.error(f"Ошибка при создании перевала: {e}")
            self.connection.rollback()
            return None

    def create_difficulty_level(self, pass_id: int, winter: str,
                                spring: str, summer: str, autumn: str) -> bool:
        """
        Создать уровни сложности для перевала.

        Args:
            pass_id: ID перевала
            winter: сложность зимой
            spring: сложность весной
            summer: сложность летом
            autumn: сложность осенью

        Returns:
            True если успешно, False если ошибка
        """
        query = """
            INSERT INTO difficulty_levels (pass_id, winter, spring, summer, autumn)
            VALUES (%s, %s, %s, %s, %s);
        """

        return self.execute_query(query, (pass_id, winter, spring, summer, autumn))

    def create_image(self, pass_id: int, title: str, image_data: bytes) -> bool:
        """
        Сохранить фотографию в БД.

        Args:
            pass_id: ID перевала
            title: название фото
            image_data: данные изображения (байты)

        Returns:
            True если успешно, False если ошибка
        """
        query = """
            INSERT INTO images (pass_id, title, data)
            VALUES (%s, %s, %s);
        """

        return self.execute_query(query, (pass_id, title, image_data))

    def submit_pass_data(self, pass_data: Dict[str, Any]) -> Tuple[int, Optional[str], Optional[int]]:
        """
        Главный метод для добавления информации о перевале в БД.
        Это метод вызывается из REST API.

        Args:
            pass_data: словарь с информацией о перевале

        Returns:
            Кортеж (status_code, message, pass_id)
            - status_code: 200 (успех), 400 (ошибка валидации), 500 (ошибка БД)
            - message: сообщение об ошибке (если есть)
            - pass_id: ID вставленного перевала (если успех)
        """

        # Подключаемся к БД
        if not self.connect():
            return 500, "Ошибка подключения к базе данных", None

        try:
            # Извлекаем данные пользователя
            user_data = pass_data.get('user', {})
            email = user_data.get('email')
            phone = user_data.get('phone')
            fam = user_data.get('fam')
            name = user_data.get('name')
            otc = user_data.get('otc')

            # Проверяем, что все поля есть
            if not all([email, phone, fam, name, otc]):
                return 400, "Не хватает полей в данных пользователя", None

            # Создаём или получаем пользователя
            user_id = self.create_user(email, phone, fam, name, otc)
            if not user_id:
                return 500, "Ошибка при создании пользователя", None

            # Извлекаем данные перевала
            coords = pass_data.get('coords', {})
            level = pass_data.get('level', {})
            images = pass_data.get('images', [])

            beauty_title = pass_data.get('beauty_title', '')
            title = pass_data.get('title')
            other_titles = pass_data.get('other_titles', '')
            connect = pass_data.get('connect', '')
            add_time = pass_data.get('add_time')
            latitude = float(coords.get('latitude', 0))
            longitude = float(coords.get('longitude', 0))
            height = int(coords.get('height', 0))

            # Проверяем, что все обязательные поля есть
            if not all([title, add_time]):
                return 400, "Не хватает обязательных полей", None

            # Создаём перевал
            pass_id = self.create_pass(beauty_title, title, other_titles,
                                       connect, add_time, user_id,
                                       latitude, longitude, height)
            if not pass_id:
                return 500, "Ошибка при создании перевала", None

            # Добавляем уровни сложности
            self.create_difficulty_level(
                pass_id,
                level.get('winter', ''),
                level.get('spring', ''),
                level.get('summer', ''),
                level.get('autumn', '')
            )

            # Добавляем фотографии
            for image in images:
                image_title = image.get('title', '')
                image_data = image.get('data', '')

                # Декодируем Base64 данные
                try:
                    image_bytes = base64.b64decode(image_data)

                    # проверяем размер
                    if len(image_bytes) > MAX_IMAGE_SIZE:
                        logger.warning(f"Изображение '{image_title}' слишком большое, пропускаем")
                        continue

                    self.create_image(pass_id, image_title, image_bytes)

                except Exception as e:
                    logger.error(f"Ошибка при обработке изображения '{image_title}': {e}")
                    # продолжаем, даже если одно фото не загрузилось

            return 200, None, pass_id

        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return 500, "Ошибка при обработке данных", None

        finally:
            # Всегда отключаемся от БД
            self.disconnect()
