import os

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):

    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")

    DEEPSEEK_API_KEY: SecretStr
    DEEPSEEK_MODEL_NAME: str = "deepseek-chat"

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
settings = Config()  
