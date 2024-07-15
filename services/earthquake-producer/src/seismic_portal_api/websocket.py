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

    def get_earthquakes(self) -> List[dict]:
        """
        Fetches the earthquake data from the Seismic Portal Websocket API.

        Args:
            None

        Returns:
            List[dict]: A list of dictionaries with the earthquake data with the format:
                {
                    "timestamp_ms": "2021-06-01T00:00:00.000Z",
                    "lat": 34.6820,
                    "lon": 23.8458,
                    "depth": 10.3,
                    "mag": 3.0,
                    "region": "CRETE, GREECE"
                }
        """
        msg = self._ws.recv()
        msg = json.loads(msg)

        logger.debug('Received data.')

        msg_contents = msg['data']['properties']

        timestamp_ms = self.to_ms(msg_contents['time'])

        # earthquake = {
        #     'timestamp_ms': timestamp_ms,
        #     'lat': msg_contents['lat'],
        #     'lon': msg_contents['lon'],
        #     'depth': msg_contents['depth'],
        #     'mag': msg_contents['mag'],
        #     'region': msg_contents['flynn_region']
        # }
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
        A function that transforms a timestamps expressed
        as a string like this '2024-06-17T09:36:39.467866Z'
        into a timestamp expressed in milliseconds.

        Args:
            timestamp (str): A timestamp expressed as a string.

        Returns:
            int: A timestamp expressed in milliseconds.
        """
        # parse a string like this '2024-06-17T09:36:39.467866Z'
        # into a datetime object assuming UTC timezone
        # and then transform this datetime object into Unix timestamp
        # expressed in milliseconds
        from dateutil import parser
        from datetime import timezone

        timestamp = parser.isoparse(timestamp).astimezone(timezone.utc)
        return int(timestamp.timestamp() * 1000)
