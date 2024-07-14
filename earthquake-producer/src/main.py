from loguru import logger
from quixstreams import Application

from src.config import config
from src.seismic_portal_api.earthquake import Earthquake
from src.seismic_portal_api.websocket import SeismicPortalAPI

def produce_earthquakes(
        kafka_broker_address: str,
        kafka_topic: str,
        live_or_historical: str,
) -> None:
    """
    Main function that runs the Earthquake Producer.
    """

    app = Application(broker_address=kafka_broker_address)
    topic = app.topic(name=kafka_topic, value_serializer='json')

    logger.info(f'Creating a service to fetch {live_or_historical} earthquake data.')

    if live_or_historical == 'live':
        seismic_portal_api = SeismicPortalAPI()

    # else:
    #     raise NotImplementedError('Historical data is not implemented yet.')

    logger.info('Creating the kafka producer.')
    logger.debug(topic.name)

    with app.get_producer() as producer:
        while True:

            # Get the earthquakes from the Kraken API
            earthquake: Earthquake = seismic_portal_api.get_earthquakes()
            # Serialize an event using the defined Topic

            message = topic.serialize(
                key=earthquake.region,
                value=earthquake.model_dump()
            )

            producer.produce(
                topic=topic.name,
                value=message.value,
                key=message.key,
            )

            logger.debug(earthquake.model_dump())

            logger.info(earthquake)

if __name__ == '__main__':
    try:
        produce_earthquakes(
            kafka_broker_address=config.kafka_broker_address,
            kafka_topic=config.kafka_topic,
            live_or_historical=config.live_or_historical
        )
    except KeyboardInterrupt:
        logger.info('Exiting...')
