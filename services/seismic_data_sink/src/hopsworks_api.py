import hopsworks
import pandas as pd
from typing import List

from src.config import config


def push_data_to_feature_store(
    feature_group_name: str,
    feature_group_version: int,
    data: List[dict],
    online_or_offline: str,
    partition_key: str = "datestr",
) -> None:
    """
    Pushes the given `data` to the feature store, writing it to the feature group
    with name `feature_group_name` and version `feature_group_version`.

    Args:
        feature_group_name (str): The name of the feature group to write to.
        feature_group_version (int): The version of the feature group to write to.
        data (List[dict]): The data to write to the feature store.
        online_or_offline (str): Whether we are saving the `data` to the online or offline
        feature group

    Returns:
        None
    """
    # Authenticate with Hopsworks API
    project = hopsworks.login(
        project=config.hopsworks_project_name,
        api_key_value=config.hopsworks_api_key,
    )

    # Get the feature store
    feature_store = project.get_feature_store()

    # Get or create the feature group we will be saving feature data to
    # Get or create the 'transactions' feature group
    feature_group = feature_store.get_or_create_feature_group(
        name=feature_group_name,
        version=feature_group_version,
        description="Earthquake data from Seismic Portal",
        primary_key=["region"],
        partition_key=[partition_key],
        event_time="timestamp",
        online_enabled=True,
    )

    # transform the data (dict) into a pandas dataframe
    data = pd.DataFrame(data)

    # Write the data to the feature group

    feature_group.insert(
        data,
        write_options={
            "start_offline_materialization": True
            if online_or_offline == "offline"
            else False
        },
    )
