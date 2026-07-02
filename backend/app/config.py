from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "AI Agent 微信周报助手"
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'data' / 'weekly_agent.db').as_posix()}"
    reports_dir: str = str(BACKEND_DIR / "reports")
    frontend_url: str = "http://localhost:3000"
    timezone: str = "Asia/Shanghai"
    schedule_day: str = "mon"
    schedule_hour: int = 8
    schedule_minute: int = 30

    github_token: str = ""
    news_rss_urls: str = "https://news.google.com/rss/search?q=AI%20Agent&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

    server_chan_enabled: bool = True
    server_chan_sendkey: str = ""
    server_chan_api_base: str = "https://sctapi.ftqq.com"

    llm_enabled: bool = False
    llm_provider: str = "deepseek"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

