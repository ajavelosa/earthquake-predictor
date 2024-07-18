from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Config(BaseSettings):
    kafka_broker_address: Optional[str] = None
    kafka_topic: str
    kafka_consumer_group: str
    feature_group_name: str
    feature_group_version: int

    live_or_historical: Optional[str] = "live"

    create_new_consumer_group: Optional[bool] = False

    hopsworks_project_name: str
    hopsworks_api_key: str

    # buffer size to store messages in memory before writing
    # to the feature store
    buffer_size: int

    # force save to feature store every n seconds
    save_every_n_sec: int = 1

    @field_validator("live_or_historical")
    @classmethod
    def validate_live_or_historical(cls, value):
        assert value in {
            "live",
            "historical",
        }, f"Invalid value for live_or_historical: {value}"
        return value


config = Config()
