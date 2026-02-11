from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = r'C:\Users\Zhassuzak\OneDrive\Desktop\Fasyncpg tasks\.env'

class Settings(BaseSettings):
    DB_HOST : str
    DB_USER : str
    DB_PORT : int
    DB_PASSWORD : str
    DB_NAME : str

    @property
    def get_sync_engine(self):
        return f'postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    @property
    def get_async_engine(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    model_config  = SettingsConfigDict(env_file=env_path)

settings=Settings()
