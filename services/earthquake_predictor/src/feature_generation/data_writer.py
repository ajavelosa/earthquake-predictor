import os
import pandas as pd

import hopsworks
from loguru import logger
from hsfs.feature_store import FeatureStore

import great_expectations as ge
import src.feature_generation.data_preprocessing as dp

class DataWriter:
    """
    A class to read data from the Feature Store.

    The credentials are stored in environment variables.
    - HOPSWORKS_API_KEY: The API key to authenticate with Hopsworks.
    - HOPSWORKS_PROJECT_NAME: The Project Name in Hopsworks.
    """

    def __init__(
        self,
        feature_group_name: str = None,
        feature_group_version: int = None,
    ):
        """
        Initialize the FSReader.

        Args:
            feature_view_name: The name of the feature view.
            feature_view_version: The version of the feature view.
            feature_group_name: The name of the feature group.
            feature_group_version: The version of the feature group.
        """
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
            hostname_verification=False,
        )

        return project.get_feature_store()

    def write_to_feature_group(
        self,
        data: pd.DataFrame,
        feature_group_name: str,
        feature_group_version: int,
        expectation_suite: ge.core.ExpectationSuite,
    ) -> pd.DataFrame:
        """
        Writes the data to the feature group.

        Args:
            data: The data to write to the feature group.
            feature_group_name: The name of the feature group.
            feature_group_version: The version of the feature group.
            expectation_suite: The Great Expectations expectation suite
                to validate the data against.

        Returns:
            None: The data will be written to the feature group.
        """
        trans_fg = self._fs.get_or_create_feature_group(
            name=feature_group_name,
            version=feature_group_version,
            primary_key=['uuid'],
            event_time='timestamp',
            online_enabled=True,
            expectation_suite=expectation_suite,
        )

        trans_fg.insert(data)
