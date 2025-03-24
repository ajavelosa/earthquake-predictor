from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Config(BaseSettings):
    feature_group_name: str
    feature_group_version: int

    feature_view_name: str
    feature_view_version: int

    hopsworks_project_name: str
    hopsworks_api_key: str

    live_or_historical: Optional[str] = "historical"

    @field_validator("live_or_historical")
    @classmethod
    def validate_live_or_historical(cls, value):
        assert value in {
            "live",
            "historical",
        }, f"Invalid value for live_or_historical: {value}"
        return value


config = Config()
