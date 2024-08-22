from pydantic_settings import BaseSettings

class Config(BaseSettings):

    kafka_broker_address: str = "localhost:19092"
    kafka_consumer_group: str = "earthquakes_by_day_consumer_group"

    input_topic: str = "earthquakes_historical"
    output_topic: str = "earthquakes_aggregated"

    window_duration_ms: int = 60 * 60 * 1000 # 1 hour

config = Config()
