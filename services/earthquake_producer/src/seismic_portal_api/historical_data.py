import requests
import xmltodict

from loguru import logger

from typing import List, Tuple
from datetime import datetime, timedelta, timezone
from dateutil import parser
from src.seismic_portal_api.earthquake import Earthquake


class HistoricalEarthquakes:
    """
    A class to query the Seismic Portal API for historical earthquakes.
    """

    URL = "https://www.seismicportal.eu/fdsnws/event/1/query?limit={limit}&start={start_timestamp}&&end={end_timestamp}"

    def __init__(
        self,
        last_n_days: int = 30,
        limit: int = 20000,
    ):
        self.last_n_days = last_n_days
        self.limit = limit
        self.start_timestamp, self.end_timestamp = self._init_from_to_timestamps(
            self.last_n_days
        )

    def get_earthquakes(self) -> List[Earthquake]:
        """
        Query the Seismic Portal API for historical earthquakes.

        Args:
            None

        Returns:
            List[Earthquake]: A list of Earthquake models, each with the format:
                {
                    "timestamp_ms": 1721081730640,
                    "datestr": 2024-07-16
                    "region": "SOUTHERN CALIFORNIA",
                    "magnitude": 2.3,
                    "depth": 7.9,
                    "latitude": 32.8632,
                    "longitude": -116.1513
                }
        """
        # The query always pulls the latest data first. As we
        # loop, we will replace the end_timestamp with the
        # timestamp of the last earthquake we fetched.
        logger.info(
            f"Querying historical earthquakes from {self.start_timestamp} to {self.end_timestamp}."
        )

        try:
            response = requests.get(
                self.URL.format(
                    limit=self.limit,
                    start_timestamp=self.start_timestamp,
                    end_timestamp=self.end_timestamp,
                )
            )
            response.raise_for_status()
        except Exception as e:
            logger.info(f"Failed to query Seismic Portal API. Status code: {e}")

        if response.status_code == 204:
            logger.info("No more earthquakes to fetch.")
            exit(0)

        else:
            response_dict = xmltodict.parse(response.text)

            # Extract the earthquakes from the response
            earthquakes = []

            for earthquake in response_dict["q:quakeml"]["eventParameters"]["event"]:
                # if 'time' < self.end_timestamp, then replace self.end_timestamp with 'time'
                time_str = earthquake["origin"]["time"]["value"]
                ts = parser.isoparse(time_str).astimezone(timezone.utc)

                if ts < self.end_timestamp:
                    self.end_timestamp = ts

                try:
                    earthquakes.append(
                        Earthquake(
                            timestamp_sec=self.to_sec(time_str),
                            datestr=time_str[:10],
                            latitude=earthquake["origin"]["latitude"]["value"],
                            longitude=earthquake["origin"]["longitude"]["value"],
                            depth=float(earthquake["origin"]["depth"]["value"]) / 1000,
                            magnitude=earthquake["magnitude"]["mag"]["value"],
                            region=earthquake["description"]["text"],
                        )
                    )
                except KeyError:
                    logger.warning(
                        f"Skipping earthquake with missing data: {earthquake}"
                    )
                    continue

            return earthquakes

    @staticmethod
    def to_sec(timestamp: str) -> int:
        """
        A function that transforms a UTC timestamp expressed
        as a string like this '2024-06-17T09:36:39.467866Z'
        into a timestamp expressed in seconds like 1718616999.

        Args:
            timestamp (str): A timestamp expressed as a string.

        Returns:
            int: A timestamp expressed in milliseconds.
        """
        timestamp = parser.isoparse(timestamp).astimezone(timezone.utc)
        return int(timestamp.timestamp())

    @staticmethod
    def _init_from_to_timestamps(last_n_days: int) -> Tuple[datetime, datetime]:
        """
        Initializes the start and end timestamps for the query.
        """
        end_timestamp = datetime.now(timezone.utc)
        start_timestamp = end_timestamp - timedelta(days=last_n_days)
        return start_timestamp, end_timestamp
