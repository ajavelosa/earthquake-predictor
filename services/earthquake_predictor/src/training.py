import pandas as pd
from typing import Tuple

from src.data_preprocessing import train_test_split
from src.data_reader import DataReader

def train(
    feature_group_name: str,
    feature_group_version: int,
    feature_view_name: str,
    feature_view_version: int,
    last_n_days_to_fetch_from_store: int,
    last_n_days_to_test_model: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    This function trains the model using the following steps:

    1. Fetch `last_n_days_to_fetch_from_store` data from the feature store.
    2. Split the data into training and testing sets.
    3. Preprocess the data, including missing value imputation.
    4. Create the target values as a new column.
    5. Train and evaluate the model.
    6. Save the model and its artifacts to the model registry.
    """

    data_reader = DataReader(
        feature_view_name=feature_view_name,
        feature_view_version=feature_view_version,
        feature_group_name=feature_group_name,
        feature_group_version=feature_group_version,
    )

    data = data_reader.read_from_offline_store(last_n_days=last_n_days_to_fetch_from_store)

    train_data, test_data = train_test_split(data, last_n_days_to_test=last_n_days_to_test_model)


    return train_data, test_data

if __name__ == '__main__':
    train_data, test_data = train(
        feature_group_name='earthquakes',
        feature_group_version=4,
        feature_view_name='earthquakes',
        feature_view_version=4,
        last_n_days_to_fetch_from_store=30,
        last_n_days_to_test_model=7,
    )
