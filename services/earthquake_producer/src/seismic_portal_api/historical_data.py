import requests
import xmltodict

from loguru import logger

from typing import List, Tuple
from datetime import datetime, timedelta, timezone
from src.seismic_portal_api.earthquake import Earthquake
from src.seismic_portal_api.utils import to_ms, generate_earthquake_uuid


class HistoricalEarthquakes:
    """
    A class to query the Seismic Portal API for historical earthquakes.
    """

    URL = "https://www.seismicportal.eu/fdsnws/event/1/query?limit={limit}&start={start_date}&end={end_date}"

    def __init__(
        self,
        last_n_days: int = 30,
        limit: int = 20000,
    ):
        self.last_n_days = last_n_days
        self.limit = limit
        self.start_date, self.end_date = self._init_from_to_dates(self.last_n_days)

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
        # The query always pulls the latest data first. We need to query from the start so that
        # we can get the oldest data first and process the data via Quixstreams. To do this, we
        # need to query the data in chunks of 90 days. That will provide a safe buffer to ensure
        # that we don't miss any data given the batch limit of 20,000.

        start_of_batch = self.start_date
        end_of_batch = min(start_of_batch + timedelta(days=90), self.end_date)

        try:
            logger.info("Running query to Seismic Portal API.")
            response = requests.get(
                self.URL.format(
                    limit=self.limit,
                    start_date=start_of_batch,
                    end_date=end_of_batch,
                )
            )
            response.raise_for_status()

        except Exception as e:
            logger.info(f"Failed to query Seismic Portal API. Status code: {e}.")
            exit(1)

        # We have no earthquakes to fetch if:
        # 1. The response status code is 204, i.e. our query returned no results.
        # 2. The start timestamp is greater than the end timestamp.
        # 3. The batch size is less than the limit, meaning we have fetched all the earthquakes.

        if response.status_code == 204 or start_of_batch > end_of_batch:
            logger.info("No more earthquakes to fetch.")
            exit(0)

        else:
            logger.info(
                f"Downloading earthquakes from {start_of_batch} to {end_of_batch}."
            )
            response_dict = xmltodict.parse(response.text)

            # Extract the earthquakes from the response
            earthquakes = []

            for earthquake in response_dict["q:quakeml"]["eventParameters"]["event"]:
                time_str = earthquake["origin"]["time"]["value"]

                try:
                    region = earthquake["description"]["text"]
                    timestamp = to_ms(time_str)
                    magnitude = earthquake["magnitude"]["mag"]["value"]

                    uuid = generate_earthquake_uuid(
                        region,
                        timestamp,
                        magnitude
                    )
                    earthquakes.append(
                        Earthquake(
                            timestamp=timestamp,
                            datestr=time_str[:10],
                            latitude=earthquake["origin"]["latitude"]["value"],
                            longitude=earthquake["origin"]["longitude"]["value"],
                            depth=float(earthquake["origin"]["depth"]["value"]) / 1000,
                            magnitude=magnitude,
                            region=region,
                            uuid=uuid
                        )
                    )

                except KeyError:
                    logger.warning(
                        f"Skipping earthquake with missing data: {earthquake}"
                    )
                    continue

            self.start_date = end_of_batch + timedelta(days=1)

            # Sort the earthquakes by timestamp on the way out to ensure that
            # the data is processed by kafka in the correct order.
            earthquakes = sorted(earthquakes, key=lambda x: x.timestamp)

            return earthquakes

    @staticmethod
    def _init_from_to_dates(last_n_days: int) -> Tuple[datetime, datetime]:
        """
        Initializes the start and end dates for the query.
        """
        end_date = datetime.now(timezone.utc).date()
        start_date = end_date - timedelta(days=last_n_days)

        return start_date, end_date
