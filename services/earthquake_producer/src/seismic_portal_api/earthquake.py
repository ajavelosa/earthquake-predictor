from pydantic import BaseModel


class Earthquake(BaseModel):
    """
    A class that represents an Earthquake Object.
    """

    timestamp: int
    datestr: str
    region: str
    magnitude: float
    depth: float
    latitude: float
    longitude: float
