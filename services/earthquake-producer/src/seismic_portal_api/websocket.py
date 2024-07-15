import json
from typing import List

from loguru import logger
from websocket import create_connection
from src.seismic_portal_api.earthquake import Earthquake

class SeismicPortalAPI:
    """
    Class that interacts with the Seismic Portal API.
    """

    URL = 'wss://www.seismicportal.eu/standing_order/websocket'

    def __init__(self):
        logger.info('Connecting to websocket.')
        self._ws = create_connection(self.URL)
        logger.info('Successfully connected to websocket.')

    def get_earthquakes(self) -> Earthquake:
        """
        Fetches the earthquake data from the Seismic Portal Websocket API.

        Args:
            None

        Returns:
            Earthquake: An earthquake class with the format:
                {
                    "timestamp_ms": 1721081730640,
                    "region": "SOUTHERN CALIFORNIA",
                    "magnitude": 2.3,
                    "depth": 7.9,
                    "latitude": 32.8632,
                    "longitude": -116.1513
                }
        """
        msg = self._ws.recv()
        msg = json.loads(msg)

        logger.debug('Received data.')

        msg_contents = msg['data']['properties']

        timestamp_ms = self.to_ms(msg_contents['time'])

        earthquake = Earthquake(
            timestamp_ms=timestamp_ms,
            latitude=msg_contents['lat'],
            longitude=msg_contents['lon'],
            depth=msg_contents['depth'],
            magnitude=msg_contents['mag'],
            region=msg_contents['flynn_region']
        )

        return earthquake

    @staticmethod
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
        from dateutil import parser
        from datetime import timezone

        timestamp = parser.isoparse(timestamp).astimezone(timezone.utc)
        return int(timestamp.timestamp() * 1000)
