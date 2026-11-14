""" Central settings model, the values that app needs, protecting . """

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", # Relative to the root of the project
        env_file_encoding="utf-8",
    )
    database_url: str

    # SECRET_KEY in .env or in the system variables, maps to this attribute
    secret_key: SecretStr  # This avoids the secret to get printed in logs or print statements
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # S3 Configuration
    s3_bucket_name: str
    s3_region: str = "eu-north-1"
    # The creds are optional to fit into 2 different deployment scenarios
    # 1. For local dev or hosting in VPS: use credentials loaded from .env
    # 2. EC2 or ECS use IAM roles: boto3 default credential chain picks up them automatically, then no need .env
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    # Adds flexibility to user other s3 services that you can run locally
    s3_endpoint_url: str | None = None

    # This helps to protect the DB from huge image uploads
    max_upload_size_bytes: int = 5 * 1024 * 1024  # 5MBs

    posts_per_page: int = 5

    reset_token_expire_minutes: int = 60

    mail_server: str = "localhost"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True

    frontend_url: str = "http://localhost:8000"


settings = Settings()  # type: ignore[call-arg] # Loaded from .env file
