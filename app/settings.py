from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Cache(BaseModel):
    backend: str = 'inmemory'
    redis_url: str = ''
    prefix: str = 'pocket_bridge_'
    pocket_list_expiration: int = 3600
    readability_expiration: int = 3600 * 24 * 7


class Settings(BaseSettings):
    pocket_consumer_key: str
    user_tokens: dict[str, str] = {}
    cache: Cache = Cache()

    model_config = SettingsConfigDict(env_prefix='BRIDGE_', env_file='.env', env_nested_delimiter='__')


settings = Settings()
