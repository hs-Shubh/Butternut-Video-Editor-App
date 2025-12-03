import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    API_KEY: str | None = os.getenv("API_KEY") or None
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    STORAGE_ROOT: str = os.getenv("STORAGE_ROOT", "./data/uploads")
    OUTPUT_ROOT: str = os.getenv("OUTPUT_ROOT", "./data/outputs")
    ASSETS_DIR: str = os.getenv("ASSETS_DIR", "../data/assets")

    AWS_ACCESS_KEY_ID: str | None = os.getenv("AWS_ACCESS_KEY_ID") or None
    AWS_SECRET_ACCESS_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY") or None
    AWS_REGION: str | None = os.getenv("AWS_REGION") or None
    AWS_S3_BUCKET: str | None = os.getenv("AWS_S3_BUCKET") or None
    S3_ENDPOINT_URL: str | None = os.getenv("S3_ENDPOINT_URL") or None


settings = Settings()
