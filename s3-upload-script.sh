#!/bin/bash

AWS_CONFIG_FILE="~/.aws/config"

/usr/local/bin/aws s3 cp /home/pi/aws-s3-testing/test-s3.txt s3://can-bus-data-test
