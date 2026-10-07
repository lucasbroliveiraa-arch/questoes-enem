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
    # Em produção, defina explicitamente os domínios do frontend.
    cors_origins: list[str] = [
        origin.strip() for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500"
        ).split(",") if origin.strip()
    ]


settings = Settings()
