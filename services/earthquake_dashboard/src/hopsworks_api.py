import hopsworks
import pandas as pd
from hsfs.feature_group import FeatureGroup
from hsfs.feature_view import FeatureView, FeatureStoreException

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
        self.feature_store = self.project.get_feature_store()
        logger.info("Connected to Hopsworks Feature Store")

    def get_feature_group(self) -> FeatureGroup:
        """
        Gets the feature group from the Hopsworks feature store. If it does
        not exist, it creates it.
        """

        # Get the feature group to read the feature view from
        feature_group = self.feature_store.get_feature_group(
            name=self.feature_group_name,
            version=self.feature_group_version,
        )
        logger.info(f"Connected to feature group: {self.feature_group_name}")

        return feature_group

    def get_feature_view(self) -> FeatureView:
        """
        Gets the feature view from the Hopsworks feature store. If it does
        not exist, it creates it. We need the feature view in order to show
        data in the dashboard.
        """

        feature_group = self.get_feature_group()

        feature_view = self.feature_store.get_or_create_feature_view(
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
            features = pd.DataFrame(columns=feature_view.schema)

        return features

    def extract_online_features_from_feature_group(self) -> pd.DataFrame:
        """
        Extracts online features from the feature view.
        """

        feature_group = self.get_feature_group()

        return feature_group.read(online=True)
