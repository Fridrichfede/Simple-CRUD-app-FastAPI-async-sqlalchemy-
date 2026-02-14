from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = r'.env'

class Settings(BaseSettings):
    DB_HOST : str
    DB_USER : str
    DB_PASSWORD : str
    DB_NAME : str

    @property
    def get_sync_engine(self):
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}?sslmode=require'
    
    @property
    def get_async_engine(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}?sslmode=require'
    
    model_config  = SettingsConfigDict(env_file=env_path)

settings=Settings()
