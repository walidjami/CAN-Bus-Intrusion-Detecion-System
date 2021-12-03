# Raspberry Pi - AWS Setup and Commands

## Send Data from Raspberry Pi to S3

### <ins>Create IAM User and Access Keys:  
See the "AWS" project's README.md and read the section "IAM - Create RPi User"


### <ins>Install AWS CLI:  
pip install awscli


### <ins>Setup IAM User Config:  
Run this command to setup the IAM user configuration:
```
aws configure
```
	
The terminal should output the following (line by line):  
```
AWS Access Key ID [None]: <ACCESS_KEY>  
AWS Secret Access Key [None]: <SECRET_ACCESS_KEY>  
Default region name [None]: us-east-1  
Default output format [None]: <ENTER>  
```
(Use the access_key and secret_key from `rpi.user` that was downloaded in the AWS project's IAM section)



### <ins>Send File to S3:  
Test sending data to S3:  
```
aws s3 cp test.txt s3://can-bus-locally-aggregated-models
```


### <ins>Create Script to Upload to S3:  
vi s3-upload-script.sh  
```
#!/bin/bash

AWS_CONFIG_FILE="~/.aws/config"

/usr/local/bin/aws s3 cp /home/pi/aws-s3/offline_model_* s3://can-bus-locally-aggregated-models
```

Make the script executable:  
```
chmod +x s3-upload-script.sh
```


### <ins>Setup a Cron to Run the Upload Script at a Frequency: 
Edit crontab for a user:  
crontab –u <username> –e  
```
5 * * * * /home/pi/aws-s3/s3-upload-script.sh >> /home/pi/aws-s3/s3-logs.log 2>&1
```
(every 5 min)

View all crontabs for a user:  
```
crontab -u <username> -l
```