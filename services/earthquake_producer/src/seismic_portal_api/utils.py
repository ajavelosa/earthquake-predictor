from dateutil import parser
from datetime import timezone
from src.seismic_portal_api.earthquake import Earthquake

import uuid
import hashlib

def to_ms(timestamp: str) -> int:
    """
    A function that transforms a UTC timestamp expressed
    as a string like this '2024-06-17T09:36:39.467866Z'
    into a timestamp expressed in milliseconds such as
    1718616999000.

    Args:
        timestamp (str): A timestamp expressed as a string.

    Returns:
        int: A timestamp expressed in milliseconds.
    """

    timestamp = parser.isoparse(timestamp).astimezone(timezone.utc)
    return int(timestamp.timestamp()) * 1000

def generate_earthquake_uuid(region: str, timestamp: int, magnitude: float) -> str:
    """
    A function that generates a unique identifier for an earthquake.

    Args:
        earthquake (Earthquake): An Earthquake model.

    Returns:
        str: A unique identifier (UUID) for the earthquake.
    """
    uuid_str = hashlib.md5(
        f"{region}-{str(timestamp)}-{str(magnitude)}".encode()
    ).hexdigest()

    return uuid.UUID(hex=uuid_str)
