from pydantic import BaseSettings


class Settings(BaseSettings):
    # Database Config
    database_url: str = "sqlite:///db.sqlite3"
    database_echo: bool = False

    # JWT Config
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 28800  # 20 days

    # Model Prediction URL
    model_url: str = "http://localhost:8502/v1/models/muril_batchnorm_d0.5:predict"

    class Config:
        env_file = ".env"


# Import this from other files
settings = Settings()
