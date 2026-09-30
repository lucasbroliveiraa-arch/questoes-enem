"""
Configurações da aplicação, lidas de variáveis de ambiente (com defaults
sensatos para desenvolvimento local via docker-compose).
"""
import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://enem:enem@localhost:5432/enem",
    )
    static_dir: str = os.getenv(
        "STATIC_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "static"),
    )
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")


settings = Settings()
