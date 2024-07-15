# Earthquake Predictor
The earthquake predictor is an application that pulls real-time earthquake data from [seismicportal.eu](https://www.seismicportal.eu/) and predicts the next earthquake. The data and predictions can be accessed through [this dashboard](tbd).

## Table of contents
- [Getting started](#getting-started)
- [Usage](#usage)
- [Structure](#structure)

## Getting started
### Clone the repository
```
git clone https://github.com/ajavelosa/earthquake-predictor.git
```
### Install the application
*Work in progress*
### Requirements
Python 3.10+, Apache Kafka 0.10+

## Usage
### Run the application
#### Get the earthquake data
```
make run-feature-pipeline
```
#### Train a model
*Work in progress*
#### Generate a prediction
*Work in progress*

## Structure
The application follows a standard three-pipeline architecture:

- **feature pipeline:** generates features to be used by the model
- **training pipeline:** trains and generates models
- **inference pipeline:** generates predictions on unseen data

### Feature pipeline
Our feature pipeline is divided into two microservices

1. `earthquake-producer`: pulls data from [seismicportal.eu](https://www.seismicportal.eu/) and stores that data in a kafka topic
2. `kafka-to-feature-store`: consumes the data from (1) and pushes it to a Hopsworks Feature Store

### Training pipeline
*Work in progress*

### Inference pipeline
*Work in progress*
