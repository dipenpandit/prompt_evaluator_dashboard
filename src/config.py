from pydantic_settings import BaseSettings, SettingsConfigDict 

class Settings(BaseSettings):
    db: str
    db_host: str 
    db_user: str 
    db_port: str = "5432"
    db_password: str 
    api_url: str = "http://localhost:8000"
    api_key: str
    base_url: str
    llm: str 
    rag_api: str = "http://localhost:8001/rag"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @property
    def sql_alchemy_database_url(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db}"

settings = Settings()

