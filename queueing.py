import uuid


def enqueue_message(sqs_client, queue, job_id, message_body):
    queue_url = queue.url
    sqs_client.send_message(QueueUrl=queue_url,
                            MessageBody=message_body,
                            MessageGroupId=job_id,
                            MessageDeduplicationId=str(uuid.uuid4()))
    return True


def dequeue_message(queue, sqs_client):
    response = sqs_client.receive_message(
        QueueUrl=queue.url,
        AttributeNames=["All"],
        MaxNumberOfMessages=10,
        VisibilityTimeout=10,
        WaitTimeSeconds=10,
    )
    messages = response.get("Messages")
    return messages


def delete_message(queue, sqs_client, messages, job_id):
    message_count = 0
    print(f"job_id: {job_id}")
    for message in messages:
        print("message:")
        print(message)
        print()
        print('MessageGroupId')
        print(message["Attributes"]["MessageGroupId"])
        if message["Attributes"]["MessageGroupId"] == job_id:
            sqs_client.delete_message(QueueUrl=queue.url,
                                      ReceiptHandle=message["ReceiptHandle"]
                                      )
        else:
            print("there are messages from an older job in here")
        message_count += 1

        print()
        print('----')
        print()
    print(f"messages: {message_count}")
    return True
