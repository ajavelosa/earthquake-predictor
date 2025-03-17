import pandas as pd

from typing import Tuple

def train_test_split(
    data: pd.DataFrame,
    last_n_days_to_test: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split the data into training and testing sets.

    Args:
        data (pd.DataFrame): The data to split.
        last_n_days_to_test (int): The number of days to use for testing.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: The training and testing sets.
    """
    # Set a cutoff data in timestamp seconds format
    cutoff_date = data['timestamp_sec'].max() - last_n_days_to_test * 24 * 60 * 60

    # Split the data
    train = data[data['timestamp_sec'] < cutoff_date]
    test = data[data['timestamp_sec'] >= cutoff_date]

    return train, test

def generate_targets(
    data: pd.DataFrame,
    window_size_days: int,
) -> pd.Series:
    """
    Generate the target values for the data.

    Args:
        data (pd.DataFrame): The data to generate targets for.
        window_size (int): The number of days to look ahead.

    Returns:
        pd.Series: The target values.
    """
    # Sort the data
    data = data.sort_values('timestamp_sec')

    # Generate the targets
    targets = data['timestamp_sec'].shift(-window_size_days * 24 * 60 * 60) < data['timestamp_sec']

    return targets

def impute_mising_values(data: pd.DataFrame) -> pd.DataFrame:
    """
    Adds missing windows to DataFrame
    """
