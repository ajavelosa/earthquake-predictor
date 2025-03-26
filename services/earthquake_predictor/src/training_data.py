<<<<<<< HEAD
=======
import pandas as pd
from typing import Tuple

>>>>>>> c8bd1ca3f8acaa065a15e3832ac01e0e129086a7
import src.feature_generation.data_preprocessing as dp
from src.feature_generation.data_reader import DataReader
from src.feature_generation.data_writer import DataWriter

<<<<<<< HEAD
from loguru import logger

=======
>>>>>>> c8bd1ca3f8acaa065a15e3832ac01e0e129086a7
from src.config import config

def generate_training_data(
    feature_group_name: str,
    feature_group_version: int,
    feature_view_name: str,
    feature_view_version: int,
    training_feature_group_name: str,
    training_feature_group_version: int,
<<<<<<< HEAD
) -> None:
=======
) -> Tuple[pd.DataFrame, pd.DataFrame]:
>>>>>>> c8bd1ca3f8acaa065a15e3832ac01e0e129086a7
    """
    This function creates the training data and pushes it
    to the feature store.

<<<<<<< HEAD
    1. Fetch data from the feature store.
    2. Preprocess the data.
    3. Create the target values as a new column.
    4. Push the data to the training_feature_group.
    """
    # 1. Fetch data from the feature store
=======
    1. Fetch `last_n_days_to_fetch_from_store` data from the feature store.
    2. Split the data into training and testing sets.
    3. Preprocess the data, including missing value imputation.
    4. Create the target values as a new column.
    5. Train and evaluate the model.
    6. Save the model and its artifacts to the model registry.
    """

>>>>>>> c8bd1ca3f8acaa065a15e3832ac01e0e129086a7
    data_reader = DataReader(
        feature_view_name=feature_view_name,
        feature_view_version=feature_view_version,
        feature_group_name=feature_group_name,
        feature_group_version=feature_group_version,
    )

    data = data_reader.read_from_online_store()

<<<<<<< HEAD
    # 2. Preprocess the data and 3. Create the target values
    df = dp.add_features(data)

    df = df[config.training_columns]

=======
    df = dp.add_features(data)

>>>>>>> c8bd1ca3f8acaa065a15e3832ac01e0e129086a7
    df.reset_index(drop=True, inplace=True)

    expectation_suite = dp.add_expectations(feature_group_name)

<<<<<<< HEAD
    # 4. Push the data to the training_feature_group
=======
    # We will write data to the training feature group
>>>>>>> c8bd1ca3f8acaa065a15e3832ac01e0e129086a7
    data_writer = DataWriter(
        feature_group_name=training_feature_group_name,
        feature_group_version=training_feature_group_version,
    )

    data_writer.write_to_feature_group(
        data=df,
        feature_group_name=training_feature_group_name,
        feature_group_version=training_feature_group_version,
        expectation_suite=expectation_suite,
    )

<<<<<<< HEAD
    logger.info(
        f"""
        Training data has been generated and pushed to the
        {training_feature_group_name} feature group, version
        {training_feature_group_version}.
        """
    )

if __name__ == '__main__':
    try:
        generate_training_data(
            feature_group_name=config.feature_group_name,
            feature_group_version=config.feature_group_version,
            feature_view_name=config.feature_view_name,
            feature_view_version=config.feature_view_version,
            training_feature_group_name=config.training_feature_group_name,
            training_feature_group_version=config.training_feature_group_version,
    )
    except KeyboardInterrupt:
        logger.info("Exiting...")
=======
if __name__ == '__main__':
    generate_training_data(
        feature_group_name=config.feature_group_name,
        feature_group_version=config.feature_group_version,
        feature_view_name=config.feature_view_name,
        feature_view_version=config.feature_view_version,
        training_feature_group_name=config.training_feature_group_name,
        training_feature_group_version=config.training_feature_group_version,
   )
>>>>>>> c8bd1ca3f8acaa065a15e3832ac01e0e129086a7
