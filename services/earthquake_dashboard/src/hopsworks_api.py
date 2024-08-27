import hopsworks
import pandas as pd
from hsfs.feature_view import FeatureView, FeatureStoreException
from typing import List, Dict

from loguru import logger

from src.external_data.regions import get_regions


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

    def extract_offline_features_from_feature_view(self) -> pd.DataFrame:
        feature_view = self.get_feature_view()

        logger.info(
            f"Extracting offline features from feature view: {self.feature_view_name}"
        )

        try:
            features: pd.DataFrame = feature_view.get_batch_data(
                read_options={"use_hive": True}
            )

        except FeatureStoreException:
            # retry the call with the use_hive option. This is what Hopsworks recommends
            logger.info("Data not available.")

        return features

    def extract_online_features_from_feature_view(self, last_n_days) -> pd.DataFrame:
        feature_view = self.get_feature_view()

        features = feature_view.get_feature_vectors(
            entry=self.get_primary_keys(last_n_days),
            return_type="pandas",
        )

        return features

    def get_primary_keys(self, last_n_days: int) -> List[Dict]:
        """
        Returns a list of dictionaries with the primary keys (regions)
        of the rows we want to fetch.
        """
        assert last_n_days > 0, "last_n_days must be greater than 0"

        regions = get_regions(last_n_days)

        primary_keys = [{"region": region} for region in regions]

        return primary_keys
