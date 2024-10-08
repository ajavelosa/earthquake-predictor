export KAFKA_TOPIC=earthquakes_historical_aggregated
export KAFKA_CONSUMER_GROUP=earthquakes_historical_aggregated_consumer_group
export FEATURE_GROUP_NAME=earthquakes_aggregated
export FEATURE_GROUP_VERSION=1

# number of elements we save at once to the Hopsworks feature store
# For live data we want to save it to the online store as soon as possible,
# so we set this to 1
export BUFFER_SIZE=10000

# this way we tell  our `kafka_to_feature_store` service to save features to the
# offline store, because we are basically generating historical data we will use for
# training our models
export LIVE_OR_HISTORICAL=historical
export SAVE_EVERY_N_SEC=600
export CREATE_NEW_CONSUMER_GROUP=true
export PARTITION_KEY=timestamp
