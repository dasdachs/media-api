from pydantic import BaseSettings


class Settings(BaseSettings):
    file_storage: str = "tmp"
    uploaded_files_dir: str = "uploaded"
    transformed_files_dir: str = "transformed"
    api_key: str = "super_secret_key"


settings = Settings()