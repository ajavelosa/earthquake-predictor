from pydantic import BaseModel

class Earthquake(BaseModel):
    """
    A class that represents an Earthquake Object.
    """
    timestamp_ms: int
    region: str
    magnitude: float
    depth: float
    latitude: float
    longitude: float

    def model_dump(self):
        return {
            'timestamp_ms': self.timestamp_ms,
            'region': self.region,
            'magnitude': self.magnitude,
            'depth': self.depth,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
