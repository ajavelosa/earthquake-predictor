import src.feature_generation.data_preprocessing as dp
from src.feature_generation.data_reader import DataReader
from src.feature_generation.data_writer import DataWriter

from loguru import logger

from src.config import config

def generate_training_data(
    feature_group_name: str,
    feature_group_version: int,
    feature_view_name: str,
    feature_view_version: int,
    training_feature_group_name: str,
    training_feature_group_version: int,
) -> None:
    """
    This function creates the training data and pushes it
    to the feature store.

    1. Fetch data from the feature store.
    2. Preprocess the data.
    3. Create the target values as a new column.
    4. Push the data to the training_feature_group.
    """
    # 1. Fetch data from the feature store
    data_reader = DataReader(
        feature_view_name=feature_view_name,
        feature_view_version=feature_view_version,
        feature_group_name=feature_group_name,
        feature_group_version=feature_group_version,
    )

    data = data_reader.read_from_online_store()

    # 2. Preprocess the data and
    # 3. Create the target values
    df = dp.add_features(data)

    df = df[config.training_columns]

    df.reset_index(drop=True, inplace=True)

    expectation_suite = dp.add_expectations(feature_group_name)

    # 4. Push the data to the training_feature_group
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
