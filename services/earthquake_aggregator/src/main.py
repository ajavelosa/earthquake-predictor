from quixstreams import Application
from typing import Any, List, Optional, Tuple
from datetime import timedelta

from loguru import logger
from src.config import config

def main(
    kafka_broker_address: str,
    kafka_consumer_group: str,
    kafka_input_topic: str,
    kafka_output_topic: str,
    window_duration_seconds: int,
    auto_offset_reset: str = "earliest",
):
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
        auto_offset_reset=auto_offset_reset,
    )

    input_topic = app.topic(
        name=kafka_input_topic,
        value_deserializer="json",
        timestamp_extractor=custom_ts_extractor,
    )

    output_topic = app.topic(kafka_output_topic, value_serializer="json")

    sdf = app.dataframe(topic=input_topic)

    # We want to extract earthquakes with significant magnitude
    # and use earthquakes with lesser magnitudes as supporting
    # features to be used by our machine learning model.

    sdf = sdf.tumbling_window(duration_ms=timedelta(seconds=window_duration_seconds))

    sdf = sdf.reduce(initializer=init_earthquakes, reducer=reduce_earthquakes).final()

    """
    We need to transform the current schema from this:
    {
        "start": 1724281200000
        "end": 1724284800000
        "value": {
            "region": "EASTERN TURKEY"
            "magnitude": 2.3
            "depth": 6.9
            "total_earthquakes": 2
        }
    }

    to this:
    {
        "region": "EASTERN TURKEY"
        "magnitude": 2.3
        "depth": 6.9
        "total_earthquakes": 2
        "timestamp": 1724284800000
    }
    """

    sdf["region"] = sdf["value"]["region"]
    sdf["magnitude"] = sdf["value"]["magnitude"]
    sdf["depth"] = sdf["value"]["depth"]
    sdf["total_earthquakes"] = sdf["value"]["total_earthquakes"]
    sdf["timestamp"] = sdf["end"]

    sdf = sdf[["region", "magnitude", "depth", "total_earthquakes", "timestamp"]]

    sdf = sdf.update(logger.info)

    sdf = sdf.to_topic(output_topic)

    app.run(sdf)

def custom_ts_extractor(
    value: Any,
    headers: Optional[List[Tuple[str, bytes]]],
    timestamp: float,
    timestamp_type: Any,
) -> int:
    """
    Specifying a custom timestamp extractor to use the timestamp from the message payload
    instead of Kafka timestamp.

    We want to use the `timestamp_sec` field from the message value, and not the timestamp
    of the message that Kafka generates when the message is saved into the Kafka topic.

    See the Quix Streams documentation here
    https://quix.io/docs/quix-streams/windowing.html#extracting-timestamps-from-messages
    """
    return value["timestamp_sec"] * 1000

def init_earthquakes(value: dict) -> dict:
    """
    Initialize the earthquakes dictionary with the first earthquake.

    We want to keep track of the region, magnitude, depth, and total
    number of earthquakes in the region per window of time.
    """
    return {
        "region": value["region"],
        "magnitude": value["magnitude"],
        "depth": value["depth"],
        "total_earthquakes": 1,
    }

def reduce_earthquakes(agg: dict, new: dict) -> dict:
    total_earthquakes = agg["total_earthquakes"] + 1
    return {
        "region": agg["region"],
        "magnitude": max(agg["magnitude"], new["magnitude"]),
        "depth": max(agg["depth"], new["depth"]),
        "total_earthquakes": total_earthquakes,
    }

if __name__ == "__main__":
    main(
        kafka_broker_address=config.kafka_broker_address,
        kafka_consumer_group=config.kafka_consumer_group,
        kafka_input_topic=config.input_topic,
        kafka_output_topic=config.output_topic,
        window_duration_seconds=config.window_duration_seconds,
    )
