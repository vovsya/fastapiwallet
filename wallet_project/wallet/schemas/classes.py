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