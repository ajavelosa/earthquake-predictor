import pandas as pd
from datetime import datetime as dt

import great_expectations as ge
from great_expectations.core import ExpectationConfiguration

def add_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Returns the the dataframe with the following features:
    - next_earthquake_magnitude
    - next_earthquake_timestamp
    - time_to_next_earthquake_ms

    Args:
        data (pd.DataFrame): The data to use.

    Returns:
        data (pd.DataFrame): The data with the next earthquake time.
    """
    new_data = data.copy()
    new_data.sort_values(['region', 'timestamp'], ascending=True, inplace=True)

    # Get year, month, and day of earthquake
    new_data['year'] = new_data['timestamp'].apply(lambda x: get_time_value(x, 'year'))
    new_data['month'] = new_data['timestamp'].apply(lambda x: get_time_value(x, 'month'))
    new_data['day'] = new_data['timestamp'].apply(lambda x: get_time_value(x, 'day'))

    # Label earthquake as significant if magnitude >= 5.0
    new_data['is_significant'] = new_data['magnitude'].apply(lambda x: 1 if x >=5 else 0)

    # Get the next earthquake magnitude, timestamp, and time to next earthquake
    new_data['next_timestamp'] = new_data.groupby('region')['timestamp'].shift(-1)
    new_data['next_magnitude'] = new_data.groupby('region')['magnitude'].shift(-1)
    new_data['time_to_next_days'] = (
        (new_data['next_timestamp'] - new_data['timestamp']) / (1000 * 60 * 60 * 24)
    ).fillna(0).astype(int)

    return new_data

def get_time_value(timestamp: int, time_value: str) -> int:
    """
    Parses the timestamp to get the year, month, or day.

    Args:
        timestamp (int): The timestamp to parse in milliseconds.
        time_value (str): The time value to get.

    Returns:
        int: The year, month, or day as an integer
    """
    timestamp = timestamp / 1000

    match time_value:
        case 'year':
            return dt.fromtimestamp(timestamp).year
        case 'month':
            return dt.fromtimestamp(timestamp).month
        case 'day':
            return dt.fromtimestamp(timestamp).day

def get_last_n_entries(data: pd.DataFrame, column_name: str, n: int) -> pd.DataFrame:
    """
    Adds columns for the last n entries in the data.ejhgcbkthvdrifdlgdjrcfrdbkketirfiiighbbeftdi
    ej

    Args:
        data (pd.DataFrame): The data to use.
        n (int): The number of entries to add.

    Returns:
        pd.DataFrame: The data with a column for each of the last n entries.
    """
    for i in range(1, n+1):
        data[f'{column_name}_t_minus_{i}'] = data.groupby('region')[column_name].shift(i)

    return data

def add_expectations(
    feature_group_name: str,
) -> pd.Series:
    """
    Adds a data validation step for the pipeline.

    Args:
        data (pd.DataFrame): The data to validate.

    Returns:
        pd.Series: The target values.
    """
    # Set context
    context = ge.get_context()

    # Create expectations
    expectation_suite = context.add_expectation_suite(
        expectation_suite_name=f"{feature_group_name}_expectation_suite"
    )

    is_significant_expectation = ExpectationConfiguration(
        expectation_type="expect_column_distinct_values_to_be_in_set",
        kwargs={
            "column": "is_significant",
            "value_set": [0, 1],
        },
    )
    uuid_expectation = ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_unique",
        kwargs={
            "column": "uuid",
        },
    )
    timestamp_expectation = ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={
            "column": "timestamp",
        },
    )
    magnitude_expectation = ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={
            "column": "magnitude",
            "min_value": 0,
            "max_value": 15,
        },
    )

    expectation_suite.add_expectation(is_significant_expectation)
    expectation_suite.add_expectation(uuid_expectation)
    expectation_suite.add_expectation(timestamp_expectation)
    expectation_suite.add_expectation(magnitude_expectation)

    return expectation_suite
