from pydantic import Field
from pydantic_settings import BaseSettings


class Env(BaseSettings):
    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'

    BOT_TOKEN: str = Field(..., env='BOT_TOKEN')

    METRICS_DSN: str | None = Field(None, env='METRICS_DSN')
    METRICS_TABLE_NAME: str | None = Field(None, env='METRICS_TABLE_NAME')

    # Shared

    # Main
    MAIN_CHAT_ID: int = Field(..., env='MAIN_CHAT_ID')

    JOB_CHANNEL_ID: int | None = Field(None, env='JOB_CHANNEL_ID')

    MAIN_CAPTCHA_TTL: int = Field(300, env='MAIN_CAPTCHA_TTL')
    MAIN_CAPTCHA_QUESTION: str = Field(..., env='MAIN_CAPTCHA_QUESTION')
    MAIN_CAPTCHA_ANSWERS: list[str] = Field(..., env='MAIN_CAPTCHA_ANSWERS')
    MAIN_CAPTCHA_RIGHT_ANSWER: str = Field(..., env='MAIN_CAPTCHA_RIGHT_ANSWER')
    MAIN_CAPTCHA_WRONG_ANSWER_ALERT: str = Field(..., env='MAIN_CAPTCHA_WRONG_ANSWER_ALERT')
    MAIN_CAPTCHA_WRONG_RIGHT_ALERT: str = Field(..., env='MAIN_CAPTCHA_WRONG_RIGHT_ALERT')
    MAIN_CAPTCHA_WRONG_ANSWER_LIST: list[str] = Field(..., env='MAIN_CAPTCHA_WRONG_ANSWER_LIST')

    # Flood
    FLOOD_CHAT_ID: int | None = Field(None, env='FLOOD_CHAT_ID')

    # Admin
    ADMIN_CHAT_ID: int | None = Field(None, env='ADMIN_CHAT_ID')


env = Env()
