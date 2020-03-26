import boto3
import uuid
import json
from faker import Faker
fake = Faker()

sqs = boto3.resource('sqs', region_name='us-west-2', endpoint_url="http://localhost:4576")
sqs_client = boto3.client('sqs', region_name="us-west-2", endpoint_url="http://localhost:4576")
queue = sqs.get_queue_by_name(QueueName='movie-load.fifo')
print(queue.url)


def generate_movies(movie_count):
    movies_payload = []

    for counter in range(movie_count):
        movie = {
            "title": f"{fake.first_name()} Loves {fake.first_name()}",
            "year": 2999,
            "director": fake.name(),
            "actor": fake.name()
        }

        movies_payload.append(movie)
    return movies_payload


def enqueue_message(job_id, message_body):
    queue_url = queue.url
    sqs_client.send_message(QueueUrl=queue_url,
                            MessageBody=message_body,
                            MessageGroupId=job_id,
                            MessageDeduplicationId=str(uuid.uuid4()))


def main():

    # generate
    job_id = str(uuid.uuid4())
    movies_payloads = generate_movies(1)

    # send message to queue
    for movies_payload in movies_payloads:
        enqueue_message(job_id, json.dumps(movies_payload, sort_keys=True, indent=4))

    # receive message
    response = sqs_client.receive_message(
        QueueUrl=queue.url,
        MaxNumberOfMessages=10,
        VisibilityTimeout=10,
        WaitTimeSeconds=10,
    )

    messages = response.get("Messages")

    print(messages)

if __name__ == '__main__':
    main()