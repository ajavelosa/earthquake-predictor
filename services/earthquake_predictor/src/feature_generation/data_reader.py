from typing import Optional, List, Dict
import time
import os
import pandas as pd

import hopsworks
from loguru import logger
from hsfs.feature_store import FeatureStore
from hsfs.feature_group import FeatureGroup
from hsfs.feature_view import FeatureView

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
        self._fg = self._get_feature_group()
        self._fv = self._get_feature_view()

    @staticmethod
    def _get_feature_store() -> FeatureStore:
        """
        Returns the feature store object that we will use to read our OHLC data.
        """
        project = hopsworks.login(
            project=os.environ['HOPSWORKS_PROJECT_NAME'],
            api_key_value=os.environ['HOPSWORKS_API_KEY'],
            hostname_verification=False,
        )

        return project.get_feature_store()

    def _get_feature_group(self) -> FeatureGroup:
        """
        Gets the feature group from the Hopsworks feature store. If it does
        not exist, it creates it.
        """

        # Get the feature group to read the feature view from
        feature_group = self._fs.get_feature_group(
            name=self.feature_group_name,
            version=self.feature_group_version,
        )
        logger.info(f"Connected to feature group: {self.feature_group_name}")

        return feature_group

    def _get_feature_view(self) -> FeatureView:
        """
        Returns the feature view object that reads data from the feature store.
        """
         # Get the feature group to read the feature view from
        feature_group = self._fg

        feature_view = self._fs.get_or_create_feature_view(
            name=self.feature_view_name,
            version=self.feature_view_version,
            query=feature_group.select_all(),
        )

        logger.info(f"Retrieved feature view: {self.feature_view_name}")

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
        to_timestamp = int(time.time())
        from_timestamp = to_timestamp - last_n_days * 24 * 60 * 60

        features = self._fv.get_batch_data(
            start_time=from_timestamp,
            end_time=to_timestamp,
        )

        return features

    def read_from_online_store(self) -> pd.DataFrame:
        """
        Reads data from the online feature store.
        """
        return self._fg.read(online=True)
