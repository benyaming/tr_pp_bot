from os import getenv

from pydantic import BaseSettings, Field


class Env(BaseSettings):
    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'

    BOT_TOKEN: str = Field(..., env='BOT_TOKEN')

    IS_PROD: bool = Field(False, env='IS_PROD')

    METRICS_DSN: str | None = Field(None, env='METRICS_DSN')
    METRICS_TABLE_NAME: str | None = Field(None, env='METRICS_TABLE_NAME')

    CAPTCHA_TTL: int = Field(300, env='CAPTCHA_TTL')
    CAPTCHA_QUESTION: str = Field(..., env='CAPTCHA_QUESTION')
    CAPTCHA_ANSWERS: list[str] = Field(..., env='CAPTCHA_ANSWERS')
    CAPTCHA_RIGHT_ANSWER: str = Field(..., env='CAPTCHA_RIGHT_ANSWER')
    CAPTCHA_WRONG_ANSWER_ALERT: str = Field(..., env='CAPTCHA_WRONG_ANSWER_ALERT')
    CAPTCHA_WRONG_RIGHT_ALERT: str = Field(..., env='CAPTCHA_WRONG_RIGHT_ALERT')
    CAPTCHA_WRONG_ANSWER_LIST: list[str] = Field(..., env='CAPTCHA_WRONG_ANSWER_LIST')


env = Env()
