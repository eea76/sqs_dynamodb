import uuid
import json
import boto3

sqs = boto3.resource('sqs', region_name='us-west-2', endpoint_url="http://localhost:4576")
sqs_client = boto3.client('sqs', region_name="us-west-2", endpoint_url="http://localhost:4576")
queue = sqs.get_queue_by_name(QueueName='movie-load.fifo')

print(f"Queue URL: {queue.url}")


def enqueue_message(job_id, message_body):
    queue_url = queue.url
    sqs_client.send_message(QueueUrl=queue_url,
                            MessageBody=message_body,
                            MessageGroupId=job_id,
                            MessageDeduplicationId=str(uuid.uuid4()))
    return True


def dequeue_message():
    response = sqs_client.receive_message(
        QueueUrl=queue.url,
        AttributeNames=["All"],
        MaxNumberOfMessages=10,
        VisibilityTimeout=10,
        WaitTimeSeconds=10,
    )
    messages = response.get("Messages")
    return messages


def delete_message(messages, job_id):
    message_count = {
        "total_messages": 0,
        "deleted_messages": {},
        "undeleted_messages": {}
    }

    for message in messages:

        if message["Attributes"]["MessageGroupId"] == job_id:

            sqs_client.delete_message(QueueUrl=queue.url,
                                      ReceiptHandle=message["ReceiptHandle"]
                                      )

            if job_id not in message_count["deleted_messages"]:
                message_count["deleted_messages"][job_id] = 1
            else:
                message_count["deleted_messages"][job_id] += 1

        else:
            undeleted_message = (json.loads(message["Body"])["job_id"])
            if undeleted_message not in message_count["undeleted_messages"]:
                message_count["undeleted_messages"][undeleted_message] = 1
            else:
                message_count["undeleted_messages"][undeleted_message] += 1
        message_count["total_messages"] += 1



    return message_count
