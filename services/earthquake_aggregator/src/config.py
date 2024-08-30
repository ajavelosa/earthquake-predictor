from pydantic_settings import BaseSettings
from typing import Optional

class Config(BaseSettings):

    kafka_broker_address: Optional[str] = None
    kafka_consumer_group: str

    input_topic: str
    output_topic: str

    window_duration_seconds: int = 60 * 60 # 1 hour

config = Config()
