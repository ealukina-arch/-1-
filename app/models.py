"""
Модели данных для REST API по перевалам.
Эти классы используются для валидации входящих данных от мобильного приложения.
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserData(BaseModel):
    """
    Модель данных пользователя.
    Содержит информацию о человеке, отправившем данные о перевале.
    """
    email: EmailStr  # email должен быть валидным
    phone: str = Field(..., min_length=5, max_length=20)  # телефон
    fam: str = Field(..., min_length=1, max_length=100)   # фамилия
    name: str = Field(..., min_length=1, max_length=100)  # имя
    otc: str = Field(..., min_length=1, max_length=100)   # отчество

    class Config:
        json_schema_extra = {
            "example": {
                "email": "qwerty@mail.ru",
                "phone": "+7 555 55 55",
                "fam": "Пупкин",
                "name": "Василий",
                "otc": "Иванович"
            }
        }


class ImageData(BaseModel):
    """
    Модель для фотографии перевала.
    """
    data: str  # фото в формате Base64
    title: str = Field(..., min_length=1, max_length=255)  # название фото

    class Config:
        json_schema_extra = {
            "example": {
                "data": "base64encodedimagedata",
                "title": "Седловина"
            }
        }


class DifficultyLevel(BaseModel):
    """
    Модель для уровней сложности по сезонам.
    """
    winter: Optional[str] = Field(default="", max_length=5)
    spring: Optional[str] = Field(default="", max_length=5)
    summer: Optional[str] = Field(default="", max_length=5)
    autumn: Optional[str] = Field(default="", max_length=5)

    class Config:
        json_schema_extra = {
            "example": {
                "winter": "",
                "spring": "1А",
                "summer": "1А",
                "autumn": ""
            }
        }


class CoordinatesData(BaseModel):
    """
    Модель для координат перевала.
    """
    latitude: str  # широта
    longitude: str  # долгота
    height: str  # высота в метрах

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": "45.3842",
                "longitude": "7.1525",
                "height": "1200"
            }
        }


class SubmitPassData(BaseModel):
    """
    Главная модель для отправки данных о перевале.
    Это структура JSON, которую отправляет мобильное приложение.
    """
    beauty_title: str = Field(..., max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    other_titles: Optional[str] = Field(default="", max_length=255)
    connect: Optional[str] = Field(default="")
    add_time: str  # формат: "2021-09-22 13:18:13"
    user: UserData
    coords: CoordinatesData
    level: DifficultyLevel
    images: List[ImageData] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "beauty_title": "пер.",
                "title": "Пхия",
                "other_titles": "Триев",
                "connect": "",
                "add_time": "2021-09-22 13:18:13",
                "user": {
                    "email": "qwerty@mail.ru",
                    "phone": "+7 555 55 55",
                    "fam": "Пупкин",
                    "name": "Василий",
                    "otc": "Иванович"
                },
                "coords": {
                    "latitude": "45.3842",
                    "longitude": "7.1525",
                    "height": "1200"
                },
                "level": {
                    "winter": "",
                    "spring": "1А",
                    "summer": "1А",
                    "autumn": ""
                },
                "images": [
                    {"data": "base64imagedata", "title": "Седловина"},
                    {"data": "base64imagedata", "title": "Подъём"}
                ]
            }
        }


class SubmitPassResponse(BaseModel):
    """
    Модель ответа от REST API.
    """
    status: int  # 200, 400 или 500
    message: Optional[str]  # описание ошибки или сообщение об успехе
    id: Optional[int] = None  # ID вставленной записи (если успех)
