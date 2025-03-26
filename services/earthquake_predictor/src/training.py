import pandas as pd
from typing import Tuple

import src.feature_generation.data_preprocessing as dp
from src.feature_generation.data_reader import DataReader
from src.feature_generation.data_writer import DataWriter

from src.config import config


def train(
    training_feature_group_name: str,
    training_feature_group_version: int,
    training_feature_view_name: str,
    training_feature_view_version: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    This function creates the training data and pushes it
    to the feature store.

    1. Fetch `last_n_days_to_fetch_from_store` data from the feature store.
    2. Split the data into training and testing sets.
    3. Preprocess the data, including missing value imputation.
    4. Create the target values as a new column.
    5. Train and evaluate the model.
    6. Save the model and its artifacts to the model registry.
    """

    data_reader = DataReader(
        feature_view_name=training_feature_view_name,
        feature_view_version=training_feature_view_version,
        feature_group_name=training_feature_group_name,
        feature_group_version=training_feature_group_version,
    )

    data = data_reader.read_from_online_store()

    breakpoint()

if __name__ == '__main__':
    train(
        training_feature_group_name=config.training_feature_group_name,
        training_feature_group_version=config.training_feature_group_version,
        training_feature_view_name=config.training_feature_view_name,
        training_feature_view_version=config.training_feature_view_version,
   )
