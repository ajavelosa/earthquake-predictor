from pydantic import BaseModel

class Earthquake(BaseModel):
    """
    A class that represents an Earthquake Object.
    """
    timestamp_sec: int
    timestamp_hr: int
    region: str
    magnitude: float
    depth: float
    latitude: float
    longitude: float
