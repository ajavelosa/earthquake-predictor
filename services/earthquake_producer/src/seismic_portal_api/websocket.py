import json
import ssl

from loguru import logger
from websocket import create_connection
from src.seismic_portal_api.earthquake import Earthquake
from src.seismic_portal_api.utils import to_ms, generate_earthquake_uuid


class SeismicPortalAPI:
    """
    Class that interacts with the Seismic Portal API.
    """

    URL = "wss://www.seismicportal.eu/standing_order/websocket"

    def __init__(self):
        logger.info("Connecting to websocket.")
        self._ws = create_connection(self.URL, sslopt={"cert_reqs": ssl.CERT_NONE})
        logger.info("Successfully connected to the websocket.")

    def get_earthquakes(self) -> Earthquake:
        """
        Fetches the earthquake data from the Seismic Portal Websocket API.

        Args:
            None

        Returns:
            Earthquake: An Earthquake model with the format:
                {
                    "timestamp": 1721270674000,
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

        region = msg_contents["flynn_region"]
        timestamp = to_ms(msg_contents["time"])
        magnitude = msg_contents["mag"]

        uuid = generate_earthquake_uuid(
            region,
            timestamp,
            magnitude,
        )
        earthquake = Earthquake(
            timestamp=timestamp,
            datestr=msg_contents["time"][:10],
            latitude=msg_contents["lat"],
            longitude=msg_contents["lon"],
            depth=msg_contents["depth"],
            magnitude=magnitude,
            region=region,
            uuid=uuid,
        )

        return [earthquake]
