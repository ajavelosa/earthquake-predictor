import streamlit as st

from src.config import config
from src.hopsworks_api import HopsworksApi
from datetime import datetime, timezone

st.set_page_config(
    layout="wide",
    page_title="Earthquake Dashboard",
)
st.title("Earthquake Dashboard")

live_or_historical = st.radio("Live or Historical Data", ["Live", "Historical"])

hopsworks_api = HopsworksApi(
    api_key=config.hopsworks_api_key,
    project_name=config.hopsworks_project_name,
    feature_group_name=config.feature_group_name,
    feature_group_version=config.feature_group_version,
    feature_view_name=config.feature_view_name,
    feature_view_version=config.feature_view_version,
)


@st.cache_data
def get_offline_data():
    return hopsworks_api.extract_offline_features_from_feature_view()


def get_online_data(last_n_days: int = 7):
    return hopsworks_api.extract_online_features_from_feature_view(last_n_days)


historical_data = get_offline_data()
live_data = get_online_data(config.last_n_days)

if live_or_historical == "Historical":
    data = historical_data

else:
    data = live_data

# Convert timestamp in milliseconds to datetime


data["datetime"] = data["timestamp_sec"].apply(
    lambda x: datetime.fromtimestamp(x, timezone.utc)
)

data.set_index("datetime", inplace=True)

st.map(data, latitude="latitude", longitude="longitude", size="magnitude", zoom=1)
st.table(data.sort_index(ascending=False).head(50))
