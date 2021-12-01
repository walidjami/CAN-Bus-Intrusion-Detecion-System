# AWS
## Overview:
This project documents how to setup and configure all of the required AWS resources

---

## IAM:
### <ins>IAM - Create Users:
Create ec2.user  

Create rpi.user  
(This user will be used in the "Raspberry Pi" project)
 
#### <ins>IAM - Create EC2 User
ec2.user needs S3 and SQS access  
 - This user will be used in the "EC2" section of this documentation

IAM > Users > Add users
User name*  
```
ec2.user
```

Select AWS credential type*  

 - [x] Access key - Programmatic access  
(Enables an access key ID and secret access key for the AWS API, CLI, SDK, and other development tools.)


Permissions > Attach existing policies directly  
- [x] AmazonS3FullAccess
- [x] AmazonSQSFullAccess

Tags > Review > "Create user"

**Download the Credentials!!!**


#### <ins>IAM - Create RPi User
rpi.user needs S3 access **only**  
 - This user will be used in the "Raspberry Pi" section of this documentation

IAM > Users > Add users
User name*  
```
rpi.user
```

Select AWS credential type*  

 - [x] Access key - Programmatic access  
(Enables an access key ID and secret access key for the AWS API, CLI, SDK, and other development tools.)


Permissions > Attach existing policies directly  
- [x] AmazonS3FullAccess

Tags > Review > "Create user"

**Download the Credentials!!!**



### <ins> IAM - User Roles and Policies:
- rpi.user needs S3 access *only*  
- ec2.user needs S3 and SQS access  

---

## S3:
### <ins> S3 - Create Locally Aggregated Models Bucket
S3 > Create bucket  
Bucket name:  
```
can-bus-locally-aggregated-models
```  

AWS Region:  
```
us-east-1
```  

Block Public Access settings for this bucket:  
 - [x] Block all public access

Click "Create bucket".

### <ins> S3 - Create Federally Aggregated Models Bucket
S3 > Create bucket  
Bucket name:  
```
ec2-federally-aggregated-models
```  

AWS Region:  
```
us-east-1
```  

Block Public Access settings for this bucket:  
 - [x] Block all public access

Click "Create bucket".

### <ins> S3 - Create "Event Notification"
Create an "Event Notification" to send to a queue in SQS ***after*** the queue has been created (See the SQS section)

S3 > can-bus-locally-aggregated-models > Properties  

Scroll down and click "Create event notification"

Event name:  
```
new_s3_create_object
```

Event types:  
- [x] All object create events  
  (s3:ObjectCreated:*)

Destination:  
- [x] SQS  

Specify SQS queue:  
- [x] Choose from your SQS queues

SQS queue:  
```
can-bus-models-to-process
```  
(from the dropdown menu)


---

## SQS:
### <ins> SQS - Create Queue for Locally Aggregated Models
SQS > Create queue  
- [x] Standard  

Name:  
```
can-bus-models-to-process
```

Access Policy:  
- [x] Advanced  
```
{
  "Version": "2012-10-17",
  "Id": "SQS_Policy_Id_1",
  "Statement": [
    {
      "Sid": "SQS_Policy_Sid_1",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "SQS:SendMessage",
      "Resource": "arn:aws:sqs:us-east-1:625863798916:can-bus-models-to-process"
    }
  ]
}
```  
(This allows the queue access to S3.)

Click "Create queue"


---


## EC2:
### EC2 - Create Server Instance


### EC2 - Install required packages:
sudo apt install python3-pip

pip3 install boto3

pip3 install -U scikit-learn scipy matplotlib


### EC2 - ???
Configure AWS user
 - "aws configure" command


