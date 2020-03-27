import boto3
import uuid
import json
from faker import Faker
fake = Faker()

sqs = boto3.resource('sqs', region_name='us-west-2', endpoint_url="http://localhost:4576")
sqs_client = boto3.client('sqs', region_name="us-west-2", endpoint_url="http://localhost:4576")
queue = sqs.get_queue_by_name(QueueName='movie-load.fifo')
print(queue.url)


class DataLoadMessage:
    def __init__(self,
                 job_id: str,
                 payload: str
                 ):
        self.job_id = job_id
        self.payload = payload

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


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
    movies_to_generate = 1
    movies_payloads = generate_movies(movies_to_generate)

    # send message to queue
    for movies_payload in movies_payloads:
        data_load_message = DataLoadMessage(job_id, json.dumps(movies_payload))
        enqueue_message(job_id, data_load_message.toJSON())

    # receive message
    response = sqs_client.receive_message(
        QueueUrl=queue.url,
        AttributeNames=["All"],
        MaxNumberOfMessages=10,
        VisibilityTimeout=10,
        WaitTimeSeconds=10,
    )

    messages = response.get("Messages")

    # delete message from queue
    for message in messages:
        if message["Attributes"]["MessageGroupId"] == job_id:
            sqs_client.delete_message(QueueUrl=queue.url,
                                      ReceiptHandle=message["ReceiptHandle"]
                                      )



if __name__ == '__main__':
    main()