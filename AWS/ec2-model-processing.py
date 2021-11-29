import boto3
import json
import os
import time


def check_sqs_for_messages(access_key, secret_key, queue_name):
    # Get the sqs boto3 resource
    sqs = boto3.resource(
        'sqs',
        region_name='us-east-1',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Get the queue_url and queue_attributes (number of messages visible)
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    queue_url = queue.url
    queue_number_of_messages = queue.attributes.get('ApproximateNumberOfMessages')

    # Check for messages in the queue
    if int(queue_number_of_messages) > 0:
        print(f"Queue URL: {queue_url}")
        print(f"Number of messages found in the queue: {queue_number_of_messages}")
        file_name = get_messages_from_sqs(access_key, secret_key, queue_url)
        return file_name
    else:
        print(f"No messages found in the queue: {queue_name}")
        return ''


def get_messages_from_sqs(access_key, secret_key, queue_url):
    # Get the sqs boto3 client
    sqs_client = boto3.client(
        'sqs',
        region_name='us-east-1',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # ReceiveMessage SQS response
    receive_message_response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )
    print(f"receive_message response: {receive_message_response}")
    print(f"Number of messages received: {len(receive_message_response.get('Messages', []))}")

    for message in receive_message_response.get("Messages", []):
        print(f"Message: {message}")
        s3_object_key = json.loads(message['Body'])['Records'][0]['s3']['object']['key']
        print(f"s3_object_key: {s3_object_key}")

        # Capture the receipt_handle.
        receipt_handle = message['ReceiptHandle']
        print(f"Receipt Handle: {receipt_handle}")

        # Delete the message from the queue.
        delete_message_response = sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
        )
        print(f"delete_message_response: {delete_message_response}")

        return s3_object_key


def download_file_from_s3(access_key, secret_key, bucket_name, file_name):
    # Set credentials
    s3 = boto3.client(
        's3',
        region_name='us-east-1',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Download file_name from S3
    object_name = file_name
    print(f"Downloading file: {file_name}")
    s3.download_file(bucket_name, object_name, file_name)

    # Delete file_name from S3
    print(f"Deleting file: {file_name}")
    s3.delete_object(Bucket=bucket_name, Key=file_name)


def upload_file_to_s3(access_key, secret_key, bucket_name, aggregated_file_name):
    # Set credentials
    s3 = boto3.client(
        's3',
        region_name='us-east-1',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Upload the aggregated_file_name to the S3 bucket (ec2-federally-aggregated-models)
    object_name = aggregated_file_name
    print(f"Uploading the file \'{aggregated_file_name}\' to the bucket \'{bucket_name}\'")
    upload_file_response = s3.upload_file(aggregated_file_name, bucket_name, object_name)
    print(f"upload_file_response: {upload_file_response}")

    # Delete the aggregated_file_name from the local OS
    if os.path.exists(aggregated_file_name):
        os.remove(aggregated_file_name)
    else:
        print(f"The file {aggregated_file_name} does not exist.")


def main():
    # Set main variables (access keys, queue name, and bucket name)
    ACCESS_KEY = 'ACCESS_KEY'
    SECRET_KEY = 'SECRET_KEY'
    QUEUE_NAME = 'can-bus-models-to-process'
    LOCAL_BUCKET_NAME = 'can-bus-locally-aggregated-models'
    FEDERAL_BUCKET_NAME = 'ec2-federally-aggregated-models'

    count = 0

    # Infinite loop - Check queue, get S3 file_name from the queue, download and delete from S3, repeat...
    while True:
        # Check the queue for new S3 upload events in SQS
        file_name = check_sqs_for_messages(ACCESS_KEY, SECRET_KEY, QUEUE_NAME)
        print(file_name)
        if str(file_name) != '' and str(file_name) != 'None':
            # Download file and increment counter
            download_file_from_s3(ACCESS_KEY, SECRET_KEY, LOCAL_BUCKET_NAME, file_name)
            count += 1
        else:
            pass

        # Print the current count
        print(f"Current count: {count}")

        # Check the counter
        if count >= 4:
            print(f"{count} files downloaded!")
            print("Do something with downloaded files here!")
            aggregated_file_name = 'upload_test.txt'
            upload_file_to_s3(ACCESS_KEY, SECRET_KEY, FEDERAL_BUCKET_NAME, aggregated_file_name)
            print("Resetting count to 0...")
            count = 0
        else:
            pass

        # Wait 30 seconds before checking again
        print("Waiting 30 seconds...")
        time.sleep(30)


main()
