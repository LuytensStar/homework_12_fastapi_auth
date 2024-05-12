from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    postgres_db: str = 'postgres'
    postgres_user: str = 'postgres'
    postgres_password: str = '123732'
    postgres_port: str = '50000'
    sqlalchemy_database_url: str = 'postgresql+psycopg2://postgres:123732@localhost:50000/postgres'
    secret_key: str = 'secret_key'
    algorithm: str = 'HS256'
    mail_username: str = 'socageh218@meta.ua'
    mail_password: str = 'TzNwESPdJZZX8K.'
    mail_from: str = 'socageh218@meta.ua'
    mail_port: int = 465
    mail_server: str = 'smtp.meta.ua'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis: str = '6379'
    cloudinary_name: str = 'dktwtcqzn'
    cloudinary_api_key: str = '211631263487917'
    cloudinary_api_secret: str = 'hnGxzwEpi5Yd_Y8uqHMMUosLiwI'
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"



settings = Settings()
