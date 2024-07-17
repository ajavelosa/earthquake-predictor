import hopsworks
import time
import pandas as pd
from hsfs.feature_view import FeatureView, FeatureStoreException
from typing import List, Dict

from loguru import logger

class HopsworksApi:
    def __init__(
        self,
        api_key: str,
        project_name: str,
        feature_group_name: str,
        feature_group_version: int,
        feature_view_name: str,
        feature_view_version: int = 1,
    ):
        logger.info(f"Connecting to Hopsworks. Project name: {project_name}")
        self.project = hopsworks.login(
            api_key_value=api_key,
            project=project_name,
        )
        # initialize variables
        self.feature_group_name = feature_group_name
        self.feature_group_version = feature_group_version
        self.feature_view_name = feature_view_name
        self.feature_view_version = feature_view_version
        logger.info("Connected to Hopsworks")

    def get_feature_view(self) -> FeatureView:
        """
        Gets the feature view from the Hopsworks feature store. If it does
        not exist, it creates it. We need the feature view in order to show
        data in the dashboard.
        """
        feature_store = self.project.get_feature_store()

        # Get the feature group to read the feature view from
        feature_group = feature_store.get_feature_group(
            name=self.feature_group_name,
            version=self.feature_group_version,
        )
        logger.info(f"Connected to feature group: {self.feature_group_name}")

        # Get the feature view to read data from. If it does not
        # exist, create it.
        feature_view = feature_store.get_or_create_feature_view(
            name=self.feature_view_name,
            version=self.feature_view_version,
            query=feature_group.select_all(),
        )

        return feature_view

    def extract_online_features_from_feature_view(self, last_n_days) -> pd.DataFrame:

        feature_view = self.get_feature_view()

        features = feature_view.get_feature_vectors(
            entry=self.get_primary_keys(last_n_days),
            return_type="pandas",
        )

        return features

    def extract_offline_features_from_feature_view(self) -> pd.DataFrame:

        feature_view = self.get_feature_view()

        logger.info(f"Extracting offline features from feature view: {self.feature_view_name}")

        try:
            features: pd.DataFrame = feature_view.get_batch_data()

        except FeatureStoreException:
            # retry the call with the use_hive option. This is what Hopsworks recommends
            features: pd.DataFrame = feature_view.get_batch_data(
                read_options={"use_hive": True}
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
        hrs= [current_hr_utc - i for i in range(last_n_days * 24)]

        primary_keys = [
            {
                "region": "WESTERN TURKEY",
                "timestamp_hr": timestamp_hr,
            }
            for timestamp_hr in hrs
        ]

        return primary_keys