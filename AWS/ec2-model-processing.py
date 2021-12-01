import boto3
import json
import joblib
import numpy as np
import os
import time
import uuid


def check_sqs_for_messages(queue_name):
    # Get the sqs boto3 resource
    sqs = boto3.resource('sqs', region_name='us-east-1')

    # Get the queue_url and queue_attributes (number of messages visible)
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    queue_url = queue.url
    queue_number_of_messages = queue.attributes.get('ApproximateNumberOfMessages')
    print(f"Checking Queue URL: {queue_url}")

    # Check for messages in the queue
    if int(queue_number_of_messages) > 0:
        print(f"Number of messages found in the queue: {queue_number_of_messages}")
        file_name = get_messages_from_sqs(queue_url)
        print(f"File name extracted from SQS: {file_name}")
        return file_name
    else:
        print(f"No messages found in the queue: {queue_name}")
        return ''


def get_messages_from_sqs(queue_url):
    # Get the sqs boto3 client
    sqs_client = boto3.client('sqs', region_name='us-east-1')

    # ReceiveMessage SQS response
    receive_message_response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )
    # print(f"receive_message response: {receive_message_response}")
    print(f"Number of messages received: {len(receive_message_response.get('Messages', []))}")

    for message in receive_message_response.get("Messages", []):
        # print(f"Message: {message}")
        s3_object_key = json.loads(message['Body'])['Records'][0]['s3']['object']['key']
        # print(f"s3_object_key: {s3_object_key}")

        # Capture the receipt_handle.
        receipt_handle = message['ReceiptHandle']
        # print(f"Receipt Handle: {receipt_handle}")

        # Delete the message from the queue.
        delete_message_response = sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
        )
        # print(f"delete_message_response: {delete_message_response}")

        return s3_object_key


def download_file_from_s3(bucket_name, file_name):
    # Set credentials
    s3 = boto3.client('s3', region_name='us-east-1')

    # Download file_name from S3
    object_name = file_name
    print(f"Downloading file from S3: {file_name}")
    s3.download_file(bucket_name, object_name, file_name)

    # Delete file_name from S3
    print(f"Deleting file from S3: {file_name}")
    s3.delete_object(Bucket=bucket_name, Key=file_name)


def upload_file_to_s3(bucket_name, online_file_name):
    # Set credentials
    s3 = boto3.client('s3', region_name='us-east-1')

    # Upload the online_file_name to the S3 bucket (ec2-federally-aggregated-models)
    object_name = online_file_name
    print(f"Uploading the file \'{online_file_name}\' to the bucket \'{bucket_name}\'")
    upload_file_response = s3.upload_file(online_file_name, bucket_name, object_name)
    # print(f"upload_file_response: {upload_file_response}")

    # Delete the online_file_name from the local OS
    if os.path.exists(online_file_name):
        print(f"Deleting online_model file from local OS: {online_file_name}")
        os.remove(online_file_name)
    else:
        print(f"The file {online_file_name} does not exist.")


def evaluation(models_list):
    # open the four models
    model_1 = joblib.load(str(models_list[0]))
    model_2 = joblib.load(str(models_list[1]))
    model_3 = joblib.load(str(models_list[2]))
    model_4 = joblib.load(str(models_list[3]))

    # average intercepts
    avg_intercept = (model_1.intercept_ + model_2.intercept_ + model_3.intercept_ + model_4.intercept_) / 4

    # average the dual coefficients of the support vector in the decision function multiplied by their targets
    avg_dual_coef = []
    # print(model_1.dual_coef_.shape)
    # print(model_2.dual_coef_.shape)
    # print(model_3.dual_coef_.shape)
    # print(model_4.dual_coef_.shape)

    model1_dual_tp = np.transpose(model_1.dual_coef_)
    model2_dual_tp = np.transpose(model_2.dual_coef_)
    model3_dual_tp = np.transpose(model_3.dual_coef_)
    model4_dual_tp = np.transpose(model_4.dual_coef_)

    min_dual = min(len(model1_dual_tp), len(model2_dual_tp), len(model3_dual_tp), len(model4_dual_tp))
    for i in range(min_dual):  # size of min dual_coef_
        temp_dc = (model_1.dual_coef_[0][i] + model_2.dual_coef_[0][i] + model_3.dual_coef_[0][i]) / 4
        avg_dual_coef.append(temp_dc)

    # average support vectors
    avg_sv = []
    # print(model_1.support_vectors_.shape)
    # print(model_2.support_vectors_.shape)
    # print(model_3.support_vectors_.shape)
    # print(model_4.support_vectors_.shape)

    model1_sv = model_1.support_vectors_.shape[0]
    model2_sv = model_2.support_vectors_.shape[0]
    model3_sv = model_3.support_vectors_.shape[0]
    model4_sv = model_4.support_vectors_.shape[0]

    min_sv = min(model1_sv, model2_sv, model3_sv, model4_sv)
    for i in range(min_sv):
        for j in range(7):
            temp_sv = (model_1.support_vectors_[i][j] + model_2.support_vectors_[i][j] + model_3.support_vectors_[i]
                [j] +
                       model_4.support_vectors_[i][j]) / 4

            avg_sv.append(temp_sv)

    # replace values in one of the models with the averaged values
    model_4.intercept_ = avg_intercept

    for i in range(min_dual):
        model_4.dual_coef_[0][i] = avg_dual_coef[i]

    h = 0
    for i in range(min_sv):
        for j in range(7):
            model_4.support_vectors_[i][j] = avg_sv[h]
            h += 1

    online_model = model_4

    # Export online_model with UUID extension
    online_model_name = f'online_model-{str(uuid.uuid4())}'
    joblib.dump(online_model, online_model_name)

    # Delete the offline models from the local OS
    print("Deleting offline_model files from local OS.")
    for model in models_list:
        if os.path.exists(model):
            os.remove(model)
        else:
            print(f"The file {model} does not exist.")

    return online_model_name


def main():
    # Set main variables (access keys, queue name, and bucket name)
    QUEUE_NAME = 'can-bus-models-to-process'
    LOCAL_BUCKET_NAME = 'can-bus-locally-aggregated-models'
    FEDERAL_BUCKET_NAME = 'ec2-federally-aggregated-models'
    offline_models_list = []

    # Infinite loop - Check queue, get S3 file_name from the queue, download and delete from S3, repeat...
    while True:
        # Check the queue for new S3 upload events in SQS
        file_name = check_sqs_for_messages(QUEUE_NAME)
        if str(file_name) != '' and str(file_name) != 'None':
            # Download file and append the file_name to the list of offline models
            download_file_from_s3(LOCAL_BUCKET_NAME, file_name)
            offline_models_list.append(str(file_name))
        else:
            pass

        # Print the current number of offline models downloaded
        print(f"Current number of offline_models downloaded: {len(offline_models_list)}")

        # Check the number of offline models
        if len(offline_models_list) >= 4:
            print(f"\n{len(offline_models_list)} files/models downloaded!")

            # Generate the online model
            print("Generating the online model...")
            online_model_file_name = evaluation(offline_models_list)
            print("Online model generated!")

            # Upload online_model to S3
            upload_file_to_s3(FEDERAL_BUCKET_NAME, online_model_file_name)

            # Clear the offline_models_list
            # print("Clearing the local list of offline models...")
            offline_models_list.clear()
        else:
            pass

        # Wait 30 seconds before checking again
        print("Waiting 30 seconds...\n\n")
        time.sleep(30)


main()
