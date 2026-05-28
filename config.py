from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # 保持数据库配置字段不变
    db_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int

    # 统一使用小写字段命名规范
    minio_endpoint: str = Field(..., env="MINIO_ENDPOINT")
    minio_access_key: str = Field(..., env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., env="MINIO_SECRET_KEY")
    minio_bucket: str = Field(..., env="MINIO_BUCKET")
    minio_secure: bool = Field(False, env="MINIO_SECURE")
    analysis_webhook_url: str = Field(..., env="ANALYSIS_WEBHOOK_URL")
    minio_notification_queue: str = Field(..., env="MINIO_NOTIFICATION_QUEUE")

    # 删除TORTOISE_ORM属性声明
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

TORTOISE_ORM = {
    "connections": {"default": Settings().db_url},
    "apps": {
        "models": {
            "models": ["models.user",  "models.upload","models.bird_species","aerich.models"],
            "default_connection": "default",
        }
    }
}

settings = Settings()