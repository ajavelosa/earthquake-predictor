from typing import Optional, List, Dict
import time
import os
import pandas as pd

import hopsworks
from loguru import logger
from hsfs.feature_store import FeatureStore
from hsfs.feature_view import FeatureView

from src.external_data.regions import get_regions

class DataReader:
    """
    A class to read data from the Feature Store.

    The credentials are stored in environment variables.
    - HOPSWORKS_API_KEY: The API key to authenticate with Hopsworks.
    - HOPSWORKS_PROJECT_NAME: The Project Name in Hopsworks.
    """

    def __init__(
        self,
        feature_view_name: str,
        feature_view_version: int,
        feature_group_name: Optional[str] = None,
        feature_group_version: Optional[int] = None,
    ):
        """
        Initialize the FSReader.

        Args:
            feature_view_name: The name of the feature view.
            feature_view_version: The version of the feature view.
            feature_group_name: The name of the feature group.
            feature_group_version: The version of the feature group.
        """
        self.feature_view_name = feature_view_name
        self.feature_view_version = feature_view_version
        self.feature_group_name = feature_group_name
        self.feature_group_version = feature_group_version

        self._fs = self._get_feature_store()

    @staticmethod
    def _get_feature_store() -> FeatureStore:
        """
        Returns the feature store object that we will use to read our OHLC data.
        """
        project = hopsworks.login(
            project=os.environ['HOPSWORKS_PROJECT_NAME'],
            api_key_value=os.environ['HOPSWORKS_API_KEY'],
        )

        return project.get_feature_store()

    def _get_feature_view(self) -> FeatureView:
        """
        Returns the feature view object that reads data from the feature store.
        """
         # Get the feature group to read the feature view from
        feature_group = self._fs.get_feature_group(
            name=self.feature_group_name,
            version=self.feature_group_version,
        )

        logger.info(f"Connected to feature group: {self.feature_group_name}")

        feature_view = self._fs.get_or_create_feature_view(
            name=self.feature_view_name,
            version=self.feature_view_version,
            query=feature_group.select_all(),
        )

        return feature_view

    def read_from_offline_store(
        self,
        last_n_days: int,
    ) -> pd.DataFrame:
        """
        Reads data from the offline feature store.

        Args:
            last_n_days: The number of days to read data for.
        """
        to_timestamp_sec = int(time.time())
        from_timestamp_sec = to_timestamp_sec - last_n_days * 24 * 60 * 60

        feature_view = self._get_feature_view()
        features = feature_view.get_batch_data(read_options={"use_hive": True})

        features = features[features['timestamp_sec'] >= from_timestamp_sec]
        features = features[features['timestamp_sec'] <= to_timestamp_sec]

        features = features.sort_values(by='timestamp_sec').reset_index(drop=True)

        return features

    def read_from_online_store(
        self,
        last_n_days: int,
    ) -> pd.DataFrame:
        """
        Reads data from the online feature store.

        Args:
            last_n_days: The number of days to read data for.
        """
        to_timestamp_sec = int(time.time())
        from_timestamp_sec = to_timestamp_sec - last_n_days * 24 * 60 * 60

        feature_view = self._get_feature_view()
        features = feature_view.get_feature_vectors(
            entry=self.get_primary_keys(last_n_days),
            return_type="pandas",
        )

        return features

    def get_primary_keys(self, last_n_days: int) -> List[Dict]:
        """
        Returns a list of dictionaries with the primary keys (timestamps)
        of the rows we want to fetch
        """
        # Generate all hours in int for the last 'last_n_days' days

        import time

        assert last_n_days > 0, "last_n_days must be greater than 0"

        # # get the current time in seconds and floor to the last hour
        current_hr_utc = int(time.time()) // (60 * 60)

        # # generate a list of hours in int for the last 'last_n_days' days
        hrs = [current_hr_utc - i for i in range(last_n_days * 24)]
        regions = get_regions(last_n_days)

        primary_keys = [
            {
                "timestamp_hr": timestamp_hr,
                "region": region,
            }
            for region in regions
            for timestamp_hr in hrs
        ]

        return primary_keys
