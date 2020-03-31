import uuid
import json
import boto3
import logging

# logging.basicConfig(level=logging.DEBUG)

sqs = boto3.resource('sqs', region_name='us-west-2', endpoint_url="http://localhost:4576")
sqs_client = boto3.client('sqs', region_name="us-west-2", endpoint_url="http://localhost:4576")
queue = sqs.get_queue_by_name(QueueName='movie-load.fifo')

print(f"Queue URL: {queue.url}")


def send_messages_to_queue(job_id, message_body):
    queue_url = queue.url
    sqs_client.send_message(QueueUrl=queue_url,
                            MessageBody=message_body,
                            MessageGroupId=job_id,
                            MessageDeduplicationId=str(uuid.uuid4()))
    return True


def process_messages(number_of_movies):

    messages = []
    messages_processed = 0

    while True:

        response = sqs_client.receive_message(
            QueueUrl=queue.url,
            AttributeNames=['All'],
            MaxNumberOfMessages=10
        )

        try:
            messages.extend(response['Messages'])
        except KeyError:
            break

        entries = [
            {'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle']}
            for msg in response['Messages']
        ]

        messages_processed += len(entries)
        messages_remaining = number_of_movies - messages_processed
        print(f"{messages_remaining} messages remaining")

        response = sqs_client.delete_message_batch(
            QueueUrl=queue.url, Entries=entries
        )

        if len(response['Successful']) != len(entries):
            raise RuntimeError(
                f"Failed to delete messages: entries={entries!r} resp={response!r}"
            )

    return messages
