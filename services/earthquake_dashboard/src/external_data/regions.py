import requests
import xmltodict
from datetime import datetime, timedelta, timezone


def get_regions(last_n_days):
    """
    Gets all regions from a given period.
    """
    end_datetime = datetime.now(timezone.utc)
    start_datetime = end_datetime - timedelta(days=last_n_days)

    URL = "https://www.seismicportal.eu/fdsnws/event/1/query?limit={limit}&start={start_datetime}&end={end_datetime}"
    response = requests.get(
        URL.format(
            limit=20000,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
    )

    response_dict = xmltodict.parse(response.content)

    earthquake_regions = []

    for event in response_dict["q:quakeml"]["eventParameters"]["event"]:
        earthquake_regions.append(event["description"]["text"])

    return set(earthquake_regions)
