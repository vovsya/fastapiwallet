from pydantic import BaseModel, SecretStr, Field
from enum import Enum

class UserData(BaseModel):
    username: str
    password: SecretStr = Field(min_length=8, max_length=64)

class Token(BaseModel):
    access_token: str
    token_type: str

class ValueChange(str, Enum):
    PLUS    = "Добавить валюту"
    MINUS   = "Убрать валюту"

class ProfileDeletion(BaseModel):
    password1: SecretStr = Field(..., min_length=8, max_length=64, description="Введите пароль")
    password2: SecretStr = Field(..., min_length=8, max_length=64, description="Повторите пароль")
    confirm: str = Field(..., description="Введите 'ПОДТВЕРДИТЬ")