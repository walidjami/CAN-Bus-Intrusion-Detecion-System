# ECE 492 CAN Bus

## Send Data from Raspberry Pi to S3

### Create an AWS Account in IAM:  
Security credentials > "Create access key"  
Download these credentials for later use.


### Install AWS CLI:  
pip install awscli


### Configure AWS Profile:  
vi ~/.aws/config  
```
[<username>]
aws_access_key_id=<key_id>
aws_secret_access_key=<secret_key_id>
```


### Send File to S3:  
aws s3 cp test-s3.txt s3://can-bus-data-test


### Create Script to Upload to S3:  
vi s3-upload-script.sh  
```
#!/bin/bash

AWS_CONFIG_FILE="~/.aws/config"

/usr/local/bin/aws s3 cp /home/pi/aws-s3-testing/test-s3.txt s3://can-bus-data-test
```

chmod +x s3-upload-script.sh


### Setup a Cron to Run the Upload Script at a Frequency  
Edit crontab for a user:  
crontab –u <username> –e  

```
5 * * * * /home/pi/aws-s3-testing/s3-upload-script.sh >> /home/pi/aws-se-testing/s3-logs.log 2>&1
```

View all crontabs for a user:  
crontab -u <username> -l
