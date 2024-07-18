import json

from quixstreams import Application
from typing import Optional

from loguru import logger
from src.hopsworks_api import push_data_to_feature_store


def get_current_utc_sec() -> int:
    """
    Get the current time in UTC seconds.

    Returns:
        int: The current time in UTC seconds.
    """
    from datetime import datetime, timezone

    return int(datetime.now(timezone.utc).timestamp())


def kafka_to_feature_store(
    kafka_broker_address: str,
    kafka_topic: str,
    kafka_consumer_group: str,
    feature_group_name: str,
    feature_group_version: int,
    buffer_size: Optional[int] = 1,
    live_or_historical: Optional[str] = "live",
    create_new_consumer_group: Optional[bool] = False,
    save_every_n_sec: Optional[int] = 60,
) -> None:
    """
    Writes data from the `earthquake` Kafka topic and saves the data to
    our Hopsworks Feature Store.

    Args:
        kafka_broker_address: The address of the Kafka broker.
        kafka_topic: The name of the Kafka topic to read data from.
        kafka_consumer_group: The name of the Kafka consumer group.
        feature_group_name: The name of the feature group to write to.
        feature_group_version: The version of the feature group to write to.
        buffer_size: The number of messages to buffer before writing to the feature store.
        live_or_historical: Whether the data is live or historical.
        create_new_consumer_group: Whether to create a new consumer group.

    Returns:
        None
    """

    if create_new_consumer_group:
        import uuid

        kafka_consumer_group = "earthquake_historical_consumer_group_" + str(
            uuid.uuid4()
        )
        logger.debug(f"Created new Kafka consumer group: {kafka_consumer_group}")

    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
        auto_offset_reset="earliest"
        if live_or_historical == "historical"
        else "latest",
    )

    topic = app.topic(kafka_topic, value_serializer="json")

    last_saved_to_feature_store_ts = get_current_utc_sec()

    buffer = []

    # TODO: Implement the logic to write historical data to the feature store.
    # We will need to push a larger buffer size. For live, we push each message
    # immediately to the feature store since we only expect 1 message every few
    # minutes.

    with app.get_consumer() as consumer:
        consumer.subscribe(topics=[topic.name])

        while True:
            msg = consumer.poll(1)

            # Number of seconds since the last time we saved data to the feature store.
            # We will use this for buffer operations so that we push the remaining
            # elements every `save_every_n_sec` if we haven't reached the buffer size.
            since_last_saved = get_current_utc_sec() - last_saved_to_feature_store_ts

            if (msg is not None) and msg.error():
                # Log the error and continue
                logger.error(f"Kafka error: {msg.error()}")
                continue

            elif (msg is None) and (since_last_saved < save_every_n_sec):
                # Log a message and `since_last_saved` and continue
                logger.debug("No messages to process.")
                logger.debug(f"Seconds since last saved: {since_last_saved}")
                continue

            else:
                # Process the message if it exists
                if msg is not None:
                    # append the data to the buffer
                    earthquake = json.loads(msg.value().decode("utf-8"))
                    buffer.append(earthquake)
                    logger.debug(
                        f"Message was pushed to buffer. Buffer size={len(buffer)}"
                    )

                if (len(buffer) >= buffer_size) or (
                    since_last_saved >= save_every_n_sec
                ):
                    # if the buffer is not empty we write the data to the feature store
                    if len(buffer) > 0:
                        try:
                            push_data_to_feature_store(
                                feature_group_name=feature_group_name,
                                feature_group_version=feature_group_version,
                                data=buffer,
                                online_or_offline="online"
                                if live_or_historical == "live"
                                else "offline",
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to push data to the feature store: {e}"
                            )
                            continue

                        # reset the buffer
                        # Thanks Rosina!
                        buffer = []

                        last_saved_to_feature_store_ts = get_current_utc_sec()


if __name__ == "__main__":
    from src.config import config

    logger.debug("Starting Kafka to Feature Store service...")

    try:
        kafka_to_feature_store(
            kafka_topic=config.kafka_topic,
            kafka_broker_address=config.kafka_broker_address,
            kafka_consumer_group=config.kafka_consumer_group,
            feature_group_name=config.feature_group_name,
            feature_group_version=config.feature_group_version,
            buffer_size=config.buffer_size,
            live_or_historical=config.live_or_historical,
            save_every_n_sec=config.save_every_n_sec,
            create_new_consumer_group=config.create_new_consumer_group,
        )
    except KeyboardInterrupt:
        logger.info("Exiting neatly!")
