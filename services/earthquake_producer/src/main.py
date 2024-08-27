from loguru import logger
from quixstreams import Application
from typing import Optional, List

from src.config import config
from src.seismic_portal_api.earthquake import Earthquake
from src.seismic_portal_api.websocket import SeismicPortalAPI
from src.seismic_portal_api.historical_data import HistoricalEarthquakes


def produce_earthquakes(
    kafka_broker_address: str,
    kafka_topic: str,
    live_or_historical: str,
    last_n_days: Optional[int],
    limit: Optional[int],
) -> None:
    """
    Main function that runs the Earthquake Producer.
    """

    app = Application(broker_address=kafka_broker_address)
    topic = app.topic(
        name=kafka_topic,
        value_serializer="json",
    )

    logger.info(f"Creating a service to fetch {live_or_historical} earthquake data.")

    if live_or_historical == "live":
        seismic_portal_api = SeismicPortalAPI()

    else:
        seismic_portal_api = HistoricalEarthquakes(last_n_days, limit)

    logger.info("Creating the kafka producer.")
    logger.debug(topic.name)

    with app.get_producer() as producer:
        while True:
            # Get earthquakes from the seismic portal API
            earthquakes: List[Earthquake] = seismic_portal_api.get_earthquakes()

            for earthquake in earthquakes:
                message = topic.serialize(
                    key=earthquake.region, value=earthquake.model_dump()
                )
                producer.produce(
                    topic=topic.name,
                    value=message.value,
                    key=message.key,
                    timestamp=earthquake.timestamp,
                    poll_timeout=600,
                )
                logger.info(earthquake)


if __name__ == "__main__":
    try:
        produce_earthquakes(
            kafka_broker_address=config.kafka_broker_address,
            kafka_topic=config.kafka_topic,
            live_or_historical=config.live_or_historical,
            last_n_days=config.last_n_days,
            limit=config.limit,
        )
    except KeyboardInterrupt:
        logger.info("Exiting...")
