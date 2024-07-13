from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional

class Config(BaseSettings):
    kafka_broker_address: Optional[str] = None
    kafka_topic: str

    live_or_historical: str = 'live'

    @field_validator('live_or_historical')
    @classmethod
    def validate_live_or_historical(cls, value):
        assert value in {
            'live',
            'historical',
        }, f'Invalid value for live_or_historical: {value}'
        return value

config = Config()
