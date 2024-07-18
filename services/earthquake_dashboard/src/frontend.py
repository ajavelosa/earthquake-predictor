import streamlit as st

from src.config import config
from src.hopsworks_api import HopsworksApi

st.set_page_config(layout="wide")

st.title("Earthquake Dashboard")

hopsworks_api = HopsworksApi(
    api_key=config.hopsworks_api_key,
    project_name=config.hopsworks_project_name,
    feature_group_name=config.feature_group_name,
    feature_group_version=config.feature_group_version,
    feature_view_name=config.feature_view_name,
    feature_view_version=config.feature_view_version,
)

data = hopsworks_api.extract_online_features_from_feature_view(last_n_days=7)

st.map(data, latitude="latitude", longitude="longitude", size="magnitude", zoom=1)

st.table(data.head(20))
