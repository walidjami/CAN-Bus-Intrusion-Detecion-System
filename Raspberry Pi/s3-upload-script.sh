#!/bin/bash

AWS_CONFIG_FILE="~/.aws/config"

/usr/local/bin/aws s3 cp /home/pi/aws-s3/offline_model_* s3://can-bus-locally-aggregated-models
