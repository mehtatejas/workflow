from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./workflow.db", alias="DATABASE_URL")
    sql_debug: bool = Field(default=False, alias="SQL_DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
