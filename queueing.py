import uuid
import boto3
import logging

# logging.basicConfig(level=logging.DEBUG)

sqs = boto3.resource('sqs', region_name='us-east-1', endpoint_url="http://localhost:4566")
sqs_client = boto3.client('sqs', region_name="us-east-1", endpoint_url="http://localhost:4566")
queue = sqs.get_queue_by_name(QueueName='movie-load.fifo')


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
    print(f"messages to process: {number_of_movies}")
    while True:

        # todo: enable long-polling support
        # https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html

        # https: // docs.aws.amazon.com / cli / latest / reference / sqs / receive - message.html
        response = sqs_client.receive_message(
            QueueUrl=queue.url,
            AttributeNames=['All'],
            MaxNumberOfMessages=10
        )

        try:
            # https://stackoverflow.com/questions/252703/
            messages.extend(response['Messages'])
        except KeyError:
            # "Messages" does not exist in the response object aka no more messages to process
            # therefore end the loop and return messages
            break

        # todo: figure out this syntax because I still don't read list comprehensions very easily
        entries = [
            {'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle']}
            for msg in response['Messages']
        ]

        messages_processed += len(entries)
        messages_remaining = number_of_movies - messages_processed
        print(f"\t{messages_remaining} messages remaining")


        # https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_DeleteMessageBatch.html
        response = sqs_client.delete_message_batch(
            QueueUrl=queue.url,
            Entries=entries
        )


        if len(response['Successful']) != len(entries):
            raise RuntimeError(
                f"Failed to delete messages: entries={entries!r} resp={response!r}"
            )
    print(f"messages processed: {messages_processed}")
    return messages
