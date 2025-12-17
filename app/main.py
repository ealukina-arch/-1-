"""
REST API для системы управления перевалами.
Главная задача спринта: реализовать метод POST submitData.

Версия: 1.0
Автор: Туристический проект ФСТР
"""

import os
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.models import SubmitPassData, SubmitPassResponse
from app.database import Database

# Загружаем переменные окружения из файла .env
load_dotenv()

# Настраиваем логирование (один раз на всё приложение)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаём приложение FastAPI
app = FastAPI(
    title="Mountain Passes API",
    description="REST API для управления информацией о горных перевалах",
    version="1.0.0"
)


# ============== ГЛАВНЫЙ МЕТОД REST API ==============

@app.post(
    "/submitData",
    response_model=SubmitPassResponse,
    summary="Добавить информацию о перевале",
    tags=["Passes"]
)
async def submit_data(data: SubmitPassData) -> SubmitPassResponse:

    """
    Метод для отправки информации о новом перевале.

    Мобильное приложение вызывает этот метод с JSON данными о перевале.

    Args:
        data: объект SubmitPassData с информацией о перевале

    Returns:
        SubmitPassResponse с результатом (status, message, id)

    Примеры ответов:
        - {"status": 200, "message": null, "id": 42}
        - {"status": 400, "message": "Не хватает полей", "id": null}
        - {"status": 500, "message": "Ошибка БД", "id": null}
    """

    try:
        # Преобразуем объект Pydantic в словарь
        pass_data = data.model_dump()

        # Создаём объект класса Database для работы с PostgreSQL
        db = Database()

        # Вызываем метод для добавления данных в БД
        status_code, message, pass_id = db.submit_pass_data(pass_data)

        # Возвращаем ответ в нужном формате
        return SubmitPassResponse(
            status=status_code,
            message=message,
            id=pass_id
        )

    except Exception as e:
        # Если случилась непредвиденная ошибка
        logger.error(f"Ошибка в методе submit_data: {e}")
        return SubmitPassResponse(
            status=500,
            message="Внутренняя ошибка сервера при обработке запроса",
            id=None
        )


# ============== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==============

@app.get("/", tags=["Info"])
async def root():
    """
    Корневой путь API.
    Возвращает информацию о приложении.
    """
    return {
        "message": "Mountain Passes API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "POST": "/submitData - Отправить информацию о перевале",
            "GET": "/docs - Интерактивная документация",
            "GET": "/health - Проверка статуса"
        }
    }


@app.get("/health", tags=["Info"])
async def health_check():
    """
    Проверка здоровья приложения.
    Пытается подключиться к БД.
    """
    db = Database()
    if db.connect():
        db.disconnect()
        return {
            "status": "healthy",
            "database": "connected"
        }
    else:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "database": "disconnected"
            }
        )


@app.get("/docs", tags=["Info"])
async def get_docs():
    """
    Документация API.
    Автоматически генерируется FastAPI.
    Перейди на http://localhost:8000/docs
    """
    return {"message": "Документация доступна на /docs"}


# ============== ОБРАБОТКА ОШИБОК ==============

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Обработка ошибок валидации."""
    return JSONResponse(
        status_code=400,
        content={
            "status": 400,
            "message": str(exc),
            "id": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Обработка всех остальных ошибок."""
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "message": "Ошибка сервера",
            "id": None
        }
    )


# ============== ЗАПУСК ПРИЛОЖЕНИЯ ==============

if __name__ == "__main__":
    import uvicorn

    # Запускаем приложение
    # --reload: перезагружает сервер при изменении кода
    # --host: слушаем на всех интерфейсах
    # --port: используем порт 8000
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
