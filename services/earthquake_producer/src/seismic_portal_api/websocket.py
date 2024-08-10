import json

from loguru import logger
from websocket import create_connection
from src.seismic_portal_api.earthquake import Earthquake


class SeismicPortalAPI:
    """
    Class that interacts with the Seismic Portal API.
    """

    URL = "wss://www.seismicportal.eu/standing_order/websocket"

    def __init__(self):
        logger.info("Connecting to websocket.")
        self._ws = create_connection(self.URL)
        logger.info("Successfully connected to the websocket.")

    def get_earthquakes(self) -> Earthquake:
        """
        Fetches the earthquake data from the Seismic Portal Websocket API.

        Args:
            None

        Returns:
            Earthquake: An Earthquake model with the format:
                {
                    "timestamp_sec": 1721270674,
                    "datestr": 2024-07-18,
                    "region": "NEAR THE COAST OF WESTERN TURKEY",
                    "magnitude": 2.4,
                    "depth": 10,
                    "latitude": 38.96,
                    "longitude": 26.07
                }
        """
        logger.info("Listening...")
        msg = self._ws.recv()
        msg = json.loads(msg)

        logger.debug("Received data.")

        msg_contents = msg["data"]["properties"]

        timestamp_sec = self.to_sec(msg_contents["time"])

        earthquake = Earthquake(
            timestamp_sec=timestamp_sec,
            datestr=msg_contents["time"][:10],
            latitude=msg_contents["lat"],
            longitude=msg_contents["lon"],
            depth=msg_contents["depth"],
            magnitude=msg_contents["mag"],
            region=msg_contents["flynn_region"],
        )

        return [earthquake]

    @staticmethod
    def to_sec(timestamp: str) -> int:
        """
        A function that transforms a UTC timestamp expressed
        as a string like this '2024-06-17T09:36:39.467866Z'
        into a timestamp expressed in milliseconds such as
        1718616999.

        Args:
            timestamp (str): A timestamp expressed as a string.

        Returns:
            int: A timestamp expressed in seconds.
        """
        from dateutil import parser
        from datetime import timezone

        timestamp = parser.isoparse(timestamp).astimezone(timezone.utc)
        return int(timestamp.timestamp())
